"""
Extended tests for database modules to improve coverage
"""

import pytest
import tempfile
import json
import time
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import requests

from varannote.databases.dbsnp import DbSNPDatabase
from varannote.databases.omim import OMIMDatabase
from varannote.databases.hgmd import HGMDDatabase
from varannote.databases.pharmgkb import PharmGKBDatabase
from varannote.databases.ensembl import EnsemblDatabase


class TestDbSNPDatabaseExtended:
    """Extended tests for DbSNP database"""
    
    def setup_method(self):
        """Setup test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.db = DbSNPDatabase(cache_dir=self.temp_dir, use_cache=True)
    
    def teardown_method(self):
        """Cleanup test environment"""
        import shutil
        try:
            shutil.rmtree(self.temp_dir)
        except (PermissionError, OSError):
            pass
    
    def test_rate_limiting(self):
        """Test rate limiting functionality"""
        # First request should not sleep
        start_time = time.time()
        self.db._rate_limit()
        first_duration = time.time() - start_time
        
        # Second request immediately after should sleep
        start_time = time.time()
        self.db._rate_limit()
        second_duration = time.time() - start_time
        
        # Second request should take longer due to rate limiting
        assert second_duration >= first_duration
    
    def test_cache_path_generation(self):
        """Test cache path generation"""
        variant_key = "1:12345:A>G"
        cache_path = self.db._get_cache_path(variant_key)
        
        assert isinstance(cache_path, Path)
        assert "dbsnp_1_12345_A_G.json" in str(cache_path)
    
    def test_cache_operations(self):
        """Test cache save and load operations"""
        variant_key = "1:12345:A>G"
        test_data = {
            "dbsnp_id": "rs123456",
            "dbsnp_validated": True,
            "dbsnp_maf": 0.05
        }
        
        # Test save to cache
        self.db._save_to_cache(variant_key, test_data)
        
        # Test load from cache
        cached_data = self.db._load_from_cache(variant_key)
        assert cached_data == test_data
    
    def test_cache_disabled(self):
        """Test behavior when cache is disabled"""
        db_no_cache = DbSNPDatabase(cache_dir=self.temp_dir, use_cache=False)
        
        variant_key = "1:12345:A>G"
        test_data = {"dbsnp_id": "rs123456"}
        
        # Save should do nothing
        db_no_cache._save_to_cache(variant_key, test_data)
        
        # Load should return None
        cached_data = db_no_cache._load_from_cache(variant_key)
        assert cached_data is None
    
    @patch('requests.get')
    def test_search_by_coordinates_success(self, mock_get):
        """Test successful coordinate search"""
        # Mock ESearch response
        esearch_response = Mock()
        esearch_response.json.return_value = {
            "esearchresult": {"idlist": ["123456"]}
        }
        esearch_response.raise_for_status.return_value = None
        
        # Mock ESummary response
        esummary_response = Mock()
        esummary_response.json.return_value = {
            "result": {
                "123456": {
                    "rsid": "123456",
                    "validation": "true",
                    "maf": "0.05",
                    "alleles": "A/G"
                }
            }
        }
        esummary_response.raise_for_status.return_value = None
        
        mock_get.side_effect = [esearch_response, esummary_response]
        
        result = self.db._search_by_coordinates("1", 12345, "A", "G")
        
        assert result["dbsnp_id"] == "rs123456"
        assert result["dbsnp_validated"] is True
        assert result["dbsnp_maf"] == 0.05
    
    @patch('requests.get')
    def test_search_by_coordinates_no_results(self, mock_get):
        """Test coordinate search with no results"""
        # Mock ESearch response with no results
        esearch_response = Mock()
        esearch_response.json.return_value = {
            "esearchresult": {"idlist": []}
        }
        esearch_response.raise_for_status.return_value = None
        
        mock_get.return_value = esearch_response
        
        result = self.db._search_by_coordinates("1", 12345, "A", "G")
        
        assert result["dbsnp_id"] is None
        assert result["dbsnp_validated"] is None
        assert result["dbsnp_maf"] is None
    
    def test_alleles_match(self):
        """Test allele matching logic"""
        snp_data = {"alleles": "A/G"}
        
        # Should match
        assert self.db._alleles_match(snp_data, "A", "G") is True
        assert self.db._alleles_match(snp_data, "G", "A") is True
        
        # Should not match
        assert self.db._alleles_match(snp_data, "A", "T") is False
    
    def test_extract_maf(self):
        """Test MAF extraction"""
        # Valid MAF
        snp_data = {"maf": "0.05"}
        assert self.db._extract_maf(snp_data) == 0.05
        
        # Invalid MAF
        snp_data = {"maf": "invalid"}
        assert self.db._extract_maf(snp_data) is None
        
        # No MAF
        snp_data = {}
        assert self.db._extract_maf(snp_data) is None
    
    @patch('requests.get')
    def test_get_variant_annotation_with_error(self, mock_get):
        """Test variant annotation with API error"""
        mock_get.side_effect = requests.RequestException("API Error")
        
        result = self.db.get_variant_annotation("1", 12345, "A", "G")
        
        # Should return empty annotation on error
        assert result["dbsnp_id"] is None
        assert result["dbsnp_validated"] is None
        assert result["dbsnp_maf"] is None
    
    def test_get_database_info(self):
        """Test database info retrieval"""
        info = self.db.get_database_info()
        
        assert isinstance(info, dict)
        assert "name" in info
        assert "description" in info
        assert "version" in info
        assert info["name"] == "dbSNP"


class TestOMIMDatabaseExtended:
    """Extended tests for OMIM database"""
    
    def setup_method(self):
        """Setup test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.db = OMIMDatabase(api_key="test_key", cache_dir=self.temp_dir)
    
    def teardown_method(self):
        """Cleanup test environment"""
        import shutil
        try:
            shutil.rmtree(self.temp_dir)
        except (PermissionError, OSError):
            pass
    
    def test_initialization_without_api_key(self):
        """Test initialization without API key"""
        db = OMIMDatabase()
        assert db.api_key is None
    
    def test_cache_operations(self):
        """Test OMIM cache operations"""
        gene = "BRCA1"
        test_data = {
            "omim_id": "113705",
            "omim_title": "BREAST CANCER 1",
            "omim_phenotypes": ["Breast cancer"]
        }
        
        # Test save and load
        self.db._save_to_cache(gene, test_data)
        cached_data = self.db._load_from_cache(gene)
        assert cached_data == test_data
    
    @patch('requests.get')
    def test_query_omim_api_success(self, mock_get):
        """Test successful OMIM API query"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "omim": {
                "searchResponse": {
                    "geneMapList": [
                        {
                            "geneMap": {
                                "mimNumber": "113705"
                            }
                        }
                    ]
                }
            }
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = self.db._query_omim_api("BRCA1")
        
        assert isinstance(result, dict)
    
    @patch('requests.get')
    def test_get_gene_annotation_no_api_key(self, mock_get):
        """Test gene annotation without API key"""
        db = OMIMDatabase()  # No API key
        
        result = db.get_gene_annotation("BRCA1")
        
        # Should return fallback data
        assert "omim_gene_id" in result
        assert "omim_diseases" in result
    
    def test_get_database_info(self):
        """Test OMIM database info"""
        info = self.db.get_database_info()
        
        assert isinstance(info, dict)
        assert info["name"] == "OMIM"
        assert "description" in info


class TestHGMDDatabaseExtended:
    """Extended tests for HGMD database"""
    
    def setup_method(self):
        """Setup test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.db = HGMDDatabase(api_key="test_key", cache_dir=self.temp_dir)
    
    def teardown_method(self):
        """Cleanup test environment"""
        import shutil
        try:
            shutil.rmtree(self.temp_dir)
        except (PermissionError, OSError):
            pass
    
    def test_initialization_without_api_key(self):
        """Test initialization without API key"""
        db = HGMDDatabase()
        assert db.api_key is None
    
    def test_cache_operations(self):
        """Test HGMD cache operations"""
        variant_key = "1:12345:A>G"
        test_data = {
            "hgmd_id": "CM123456",
            "hgmd_class": "DM",
            "hgmd_disease": "Breast cancer"
        }
        
        # Test save and load
        self.db._save_to_cache(variant_key, test_data)
        cached_data = self.db._load_from_cache(variant_key)
        assert cached_data == test_data
    
    @patch('requests.get')
    def test_search_variant_no_api_key(self, mock_get):
        """Test variant search without API key"""
        db = HGMDDatabase()  # No API key
        
        result = db.get_variant_annotation("1", 12345, "A", "G")
        
        # Should return empty result
        assert result["hgmd_id"] is None
        assert "hgmd_disease" in result
    
    def test_get_database_info(self):
        """Test HGMD database info"""
        info = self.db.get_database_info()
        
        assert isinstance(info, dict)
        assert info["name"] == "HGMD"
        assert "description" in info


class TestPharmGKBDatabaseExtended:
    """Extended tests for PharmGKB database"""
    
    def setup_method(self):
        """Setup test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.db = PharmGKBDatabase(cache_dir=self.temp_dir)
    
    def teardown_method(self):
        """Cleanup test environment"""
        import shutil
        try:
            shutil.rmtree(self.temp_dir)
        except (PermissionError, OSError):
            pass
    
    def test_cache_operations(self):
        """Test PharmGKB cache operations"""
        gene = "CYP2D6"
        test_data = {
            "pharmgkb_id": "PA128",
            "pharmgkb_drugs": ["codeine", "tramadol"],
            "pharmgkb_phenotypes": ["poor metabolizer"]
        }
        
        # Test save and load
        self.db._save_to_cache(gene, test_data)
        cached_data = self.db._load_from_cache(gene)
        assert cached_data == test_data
    
    @patch('requests.get')
    def test_get_gene_annotation_success(self, mock_get):
        """Test successful gene annotation"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "data": [
                {
                    "objCls": "Gene",
                    "id": "PA128",
                    "name": "CYP2D6",
                    "symbol": "CYP2D6"
                }
            ]
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = self.db.get_gene_annotation("CYP2D6")
        
        assert "pharmgkb_id" in result
    
    def test_get_database_info(self):
        """Test PharmGKB database info"""
        info = self.db.get_database_info()
        
        assert isinstance(info, dict)
        assert info["name"] == "PharmGKB"
        assert "description" in info


class TestEnsemblDatabaseExtended:
    """Extended tests for Ensembl database"""
    
    def setup_method(self):
        """Setup test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.db = EnsemblDatabase(cache_dir=self.temp_dir)
    
    def teardown_method(self):
        """Cleanup test environment"""
        import shutil
        try:
            shutil.rmtree(self.temp_dir)
        except (PermissionError, OSError):
            pass
    
    def test_cache_operations(self):
        """Test Ensembl cache operations"""
        variant_key = "1:12345:A>G"
        test_data = {
            "ensembl_gene_id": "ENSG00000012048",
            "ensembl_transcript_id": "ENST00000123456",
            "ensembl_consequence": "missense_variant"
        }
        
        # Test save and load
        self.db._save_to_cache(variant_key, test_data)
        cached_data = self.db._load_from_cache(variant_key)
        assert cached_data == test_data
    
    @patch('requests.get')
    def test_get_variant_annotation_success(self, mock_get):
        """Test successful variant annotation"""
        mock_response = Mock()
        mock_response.json.return_value = [
            {
                "most_severe_consequence": "missense_variant",
                "transcript_consequences": [
                    {
                        "gene_id": "ENSG00000012048",
                        "transcript_id": "ENST00000123456",
                        "consequence_terms": ["missense_variant"]
                    }
                ]
            }
        ]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = self.db.get_variant_annotation("1", 12345, "A", "G")
        
        assert "ensembl_consequence" in result
    
    def test_get_database_info(self):
        """Test Ensembl database info"""
        info = self.db.get_database_info()
        
        assert isinstance(info, dict)
        assert info["name"] == "Ensembl"
        assert "description" in info


if __name__ == "__main__":
    pytest.main([__file__]) 