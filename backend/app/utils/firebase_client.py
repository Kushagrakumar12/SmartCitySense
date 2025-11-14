"""
Firebase Client
Handles Firebase Admin SDK initialization and provides helper methods
"""

import os
import json
import firebase_admin
from firebase_admin import credentials, firestore, auth, storage
from typing import Optional, Dict, Any, List
from datetime import datetime
import structlog

logger = structlog.get_logger()


class FirebaseClient:
    """Singleton Firebase Client"""
    
    _instance: Optional['FirebaseClient'] = None
    _initialized: bool = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._initialize_firebase()
            FirebaseClient._initialized = True
    
    def _initialize_firebase(self):
        """Initialize Firebase Admin SDK"""
        try:
            # Check if already initialized
            if firebase_admin._apps:
                logger.info("Firebase already initialized")
                self.db = firestore.client()
                return
            
            # Load credentials
            from app.config import settings
            cred_path = settings.FIREBASE_CREDENTIALS_PATH
            
            if not os.path.exists(cred_path):
                logger.error(f"Firebase credentials not found at {cred_path}")
                raise FileNotFoundError(f"Firebase credentials not found: {cred_path}")
            
            cred = credentials.Certificate(cred_path)
            
            # Initialize app
            firebase_admin.initialize_app(cred, {
                'databaseURL': settings.FIREBASE_DATABASE_URL,
                'storageBucket': settings.FIREBASE_STORAGE_BUCKET
            })
            
            self.db = firestore.client()
            logger.info("Firebase initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Firebase: {str(e)}")
            raise
    
    def get_db(self) -> firestore.Client:
        """Get Firestore client"""
        return self.db
    
    def verify_token(self, id_token: str) -> Dict[str, Any]:
        """
        Verify Firebase ID token
        
        Args:
            id_token: Firebase ID token from client
            
        Returns:
            Decoded token with user information
            
        Raises:
            auth.InvalidIdTokenError: If token is invalid
        """
        try:
            decoded_token = auth.verify_id_token(id_token)
            return decoded_token
        except Exception as e:
            logger.error(f"Token verification failed: {str(e)}")
            raise
    
    def get_user(self, uid: str) -> auth.UserRecord:
        """Get user by UID"""
        try:
            user = auth.get_user(uid)
            return user
        except Exception as e:
            logger.error(f"Failed to get user {uid}: {str(e)}")
            raise
    
    def create_user_document(self, uid: str, data: Dict[str, Any]) -> None:
        """Create or update user document in Firestore"""
        try:
            user_ref = self.db.collection('users').document(uid)
            data['updated_at'] = firestore.SERVER_TIMESTAMP
            user_ref.set(data, merge=True)
            logger.info(f"User document created/updated for {uid}")
        except Exception as e:
            logger.error(f"Failed to create user document: {str(e)}")
            raise
    
    def get_user_document(self, uid: str) -> Optional[Dict[str, Any]]:
        """Get user document from Firestore"""
        try:
            user_ref = self.db.collection('users').document(uid)
            doc = user_ref.get()
            if doc.exists:
                return doc.to_dict()
            return None
        except Exception as e:
            logger.error(f"Failed to get user document: {str(e)}")
            raise
    
    def add_document(self, collection: str, data: Dict[str, Any], doc_id: Optional[str] = None) -> str:
        """
        Add document to Firestore collection
        
        Args:
            collection: Collection name
            data: Document data
            doc_id: Optional document ID (auto-generated if not provided)
            
        Returns:
            Document ID
        """
        try:
            data['created_at'] = firestore.SERVER_TIMESTAMP
            
            if doc_id:
                doc_ref = self.db.collection(collection).document(doc_id)
                doc_ref.set(data)
                return doc_id
            else:
                doc_ref = self.db.collection(collection).add(data)
                return doc_ref[1].id
        except Exception as e:
            logger.error(f"Failed to add document to {collection}: {str(e)}")
            raise
    
    def get_document(self, collection: str, doc_id: str) -> Optional[Dict[str, Any]]:
        """Get document from Firestore"""
        try:
            doc_ref = self.db.collection(collection).document(doc_id)
            doc = doc_ref.get()
            if doc.exists:
                data = doc.to_dict()
                data['id'] = doc.id
                return data
            return None
        except Exception as e:
            logger.error(f"Failed to get document from {collection}: {str(e)}")
            raise
    
    def query_documents(
        self,
        collection: str,
        filters: Optional[List[tuple]] = None,
        order_by: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Query documents from Firestore
        
        Args:
            collection: Collection name
            filters: List of (field, operator, value) tuples
            order_by: Field to order by
            limit: Maximum number of documents
            offset: Number of documents to skip
            
        Returns:
            List of documents
        """
        try:
            query = self.db.collection(collection)
            
            # Apply filters
            if filters:
                for field, operator, value in filters:
                    query = query.where(field, operator, value)
            
            # Apply ordering
            if order_by:
                query = query.order_by(order_by)
            
            # Apply offset
            if offset:
                query = query.offset(offset)
            
            # Apply limit
            if limit:
                query = query.limit(limit)
            
            # Execute query
            docs = query.stream()
            results = []
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                results.append(data)
            
            return results
        except Exception as e:
            logger.error(f"Failed to query documents from {collection}: {str(e)}")
            raise
    
    def update_document(self, collection: str, doc_id: str, data: Dict[str, Any]) -> None:
        """Update document in Firestore"""
        try:
            doc_ref = self.db.collection(collection).document(doc_id)
            data['updated_at'] = firestore.SERVER_TIMESTAMP
            doc_ref.update(data)
            logger.info(f"Document {doc_id} updated in {collection}")
        except Exception as e:
            logger.error(f"Failed to update document: {str(e)}")
            raise
    
    def delete_document(self, collection: str, doc_id: str) -> None:
        """Delete document from Firestore"""
        try:
            doc_ref = self.db.collection(collection).document(doc_id)
            doc_ref.delete()
            logger.info(f"Document {doc_id} deleted from {collection}")
        except Exception as e:
            logger.error(f"Failed to delete document: {str(e)}")
            raise
    
    def get_collection_count(self, collection: str, filters: Optional[List[tuple]] = None) -> int:
        """Get count of documents in collection"""
        try:
            query = self.db.collection(collection)
            
            if filters:
                for field, operator, value in filters:
                    query = query.where(field, operator, value)
            
            docs = query.stream()
            return sum(1 for _ in docs)
        except Exception as e:
            logger.error(f"Failed to count documents in {collection}: {str(e)}")
            raise


# Singleton instance
firebase_client = FirebaseClient()


def get_firebase_client() -> FirebaseClient:
    """Get Firebase client instance"""
    return firebase_client
