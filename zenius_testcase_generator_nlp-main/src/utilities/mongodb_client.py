"""
MongoDB Client for Test Case Template Management
"""

import logging
from typing import Dict, List, Optional, Any
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure
from datetime import datetime

logger = logging.getLogger(__name__)

class MongoDBClient:
    """MongoDB client for managing test case templates and metadata"""
    
    def __init__(self, connection_uri: str, database_name: str = "zenius_testcase_db"):
        """
        Initialize MongoDB client
        
        Args:
            connection_uri: MongoDB connection URI
            database_name: Database name to use
        """
        self.connection_uri = connection_uri
        self.database_name = database_name
        self.client = None
        self.db = None
        
        self._connect()
    
    def _connect(self):
        """Establish connection to MongoDB"""
        try:
            self.client = MongoClient(self.connection_uri)
            self.db = self.client[self.database_name]
            
            # Test connection
            self.client.admin.command('ping')
            logger.info(f"Connected to MongoDB database: {self.database_name}")
            
        except ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    def get_template_by_type(self, test_type: str) -> Optional[Dict[str, Any]]:
        """
        Get test case template by type
        
        Args:
            test_type: Type of test case template (e.g., 'functional', 'integration')
            
        Returns:
            Template dictionary or None if not found
        """
        try:
            collection = self.db.test_templates
            template = collection.find_one({"test_type": test_type, "active": True})
            
            if template:
                # Remove MongoDB ObjectId for JSON serialization
                template.pop('_id', None)
                logger.info(f"Retrieved template for type: {test_type}")
                return template
            else:
                logger.warning(f"No template found for type: {test_type}")
                return None
                
        except OperationFailure as e:
            logger.error(f"Error retrieving template: {e}")
            return None
    
    def get_default_template(self) -> Dict[str, Any]:
        """
        Get the default test case template
        
        Returns:
            Default template dictionary
        """
        try:
            collection = self.db.test_templates
            template = collection.find_one({"is_default": True, "active": True})
            
            if template:
                template.pop('_id', None)
                logger.info("Retrieved default template")
                return template
            else:
                # Return hardcoded default if none in database
                logger.info("No default template in database, using hardcoded default")
                return self._get_hardcoded_default_template()
                
        except OperationFailure as e:
            logger.error(f"Error retrieving default template: {e}")
            return self._get_hardcoded_default_template()
    
    def _get_hardcoded_default_template(self) -> Dict[str, Any]:
        """Get hardcoded default template as fallback"""
        return {
            "template_id": "default_insurance_functional",
            "name": "Default Insurance Functional Test Template",
            "domain": "insurance",
            "test_type": "functional",
            "is_default": True,
            "fields": [
                "test_case_id",
                "test_case_title",
                "description",
                "preconditions",
                "test_steps",
                "expected_results",
                "priority",
                "test_type",
                "test_data",
                "business_rules",
                "regulatory_compliance"
            ],
            "test_types": [
                "Functional",
                "Integration",
                "Regression",
                "Performance",
                "Security",
                "Compliance"
            ],
            "priority_levels": ["High", "Medium", "Low"],
            "created_at": datetime.now().isoformat(),
            "active": True
        }
    
    def save_template(self, template: Dict[str, Any]) -> bool:
        """
        Save a test case template
        
        Args:
            template: Template dictionary to save
            
        Returns:
            True if successful, False otherwise
        """
        try:
            collection = self.db.test_templates
            
            # Add metadata
            template["created_at"] = datetime.now().isoformat()
            template["active"] = True
            
            result = collection.insert_one(template)
            
            if result.inserted_id:
                logger.info(f"Saved template: {template.get('template_id', 'unknown')}")
                return True
            else:
                logger.error("Failed to save template")
                return False
                
        except OperationFailure as e:
            logger.error(f"Error saving template: {e}")
            return False
    
    def get_all_templates(self) -> List[Dict[str, Any]]:
        """
        Get all active templates
        
        Returns:
            List of template dictionaries
        """
        try:
            collection = self.db.test_templates
            templates = list(collection.find({"active": True}))
            
            # Remove MongoDB ObjectIds
            for template in templates:
                template.pop('_id', None)
            
            logger.info(f"Retrieved {len(templates)} templates")
            return templates
            
        except OperationFailure as e:
            logger.error(f"Error retrieving templates: {e}")
            return []
    
    def save_test_case_generation_log(self, log_data: Dict[str, Any]) -> bool:
        """
        Save test case generation log for analytics
        
        Args:
            log_data: Log data dictionary
            
        Returns:
            True if successful, False otherwise
        """
        try:
            collection = self.db.generation_logs
            
            # Add timestamp
            log_data["timestamp"] = datetime.now().isoformat()
            
            result = collection.insert_one(log_data)
            
            if result.inserted_id:
                logger.info("Saved generation log")
                return True
            else:
                logger.error("Failed to save generation log")
                return False
                
        except OperationFailure as e:
            logger.error(f"Error saving generation log: {e}")
            return False
    
    def get_generation_stats(self, days: int = 30) -> Dict[str, Any]:
        """
        Get generation statistics for the last N days
        
        Args:
            days: Number of days to look back
            
        Returns:
            Statistics dictionary
        """
        try:
            from datetime import timedelta
            
            collection = self.db.generation_logs
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            # Get total generations
            total_count = collection.count_documents({
                "timestamp": {"$gte": cutoff_date}
            })
            
            # Get successful generations
            successful_count = collection.count_documents({
                "timestamp": {"$gte": cutoff_date},
                "success": True
            })
            
            # Get route distribution
            pipeline = [
                {"$match": {"timestamp": {"$gte": cutoff_date}}},
                {"$group": {"_id": "$route_taken", "count": {"$sum": 1}}}
            ]
            route_stats = list(collection.aggregate(pipeline))
            
            stats = {
                "total_generations": total_count,
                "successful_generations": successful_count,
                "success_rate": (successful_count / total_count * 100) if total_count > 0 else 0,
                "route_distribution": {item["_id"]: item["count"] for item in route_stats},
                "period_days": days,
                "generated_at": datetime.now().isoformat()
            }
            
            logger.info(f"Generated statistics for {days} days")
            return stats
            
        except Exception as e:
            logger.error(f"Error generating statistics: {e}")
            return {"error": str(e)}
    
    def close_connection(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on MongoDB connection
        
        Returns:
            Health status dictionary
        """
        try:
            # Test connection
            self.client.admin.command('ping')
            
            # Get database stats
            stats = self.db.command("dbstats")
            
            return {
                "status": "healthy",
                "database": self.database_name,
                "collections": stats.get("collections", 0),
                "data_size": stats.get("dataSize", 0),
                "storage_size": stats.get("storageSize", 0),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            } 