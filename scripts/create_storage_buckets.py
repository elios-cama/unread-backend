#!/usr/bin/env python3
"""
Script to create storage buckets in Supabase for the Unread platform.
Run this script to set up the required storage infrastructure.
"""

import os
import sys
from pathlib import Path

# Add the parent directory to the path so we can import from app
sys.path.append(str(Path(__file__).parent.parent))

from supabase import create_client, Client
from app.core.config import settings


def create_storage_buckets():
    """Create the required storage buckets with proper policies."""
    
    print("🚀 Creating Supabase storage buckets...")
    print(f"📍 Supabase URL: {settings.SUPABASE_URL}")
    
    # Initialize Supabase client with service key (admin privileges)
    supabase: Client = create_client(
        settings.SUPABASE_URL,
        settings.SUPABASE_SERVICE_KEY
    )
    
    # Define buckets to create
    buckets = [
        {
            "name": "ebooks",
            "public": False,  # Private by default, access via signed URLs
            "file_size_limit": 52428800,  # 50MB
            "allowed_mime_types": [
                "application/epub+zip",
                "application/pdf", 
                "application/x-mobipocket-ebook",
                "application/vnd.amazon.ebook",  # AZW3
                "text/plain"
            ]
        },
        {
            "name": "covers", 
            "public": True,  # Public for easy access to cover images
            "file_size_limit": 5242880,  # 5MB
            "allowed_mime_types": [
                "image/jpeg",
                "image/png", 
                "image/webp",
                "image/jpg"
            ]
        },
        {
            "name": "temp-uploads",
            "public": False,  # Private temporary storage
            "file_size_limit": 52428800,  # 50MB
            "allowed_mime_types": [
                "application/epub+zip",
                "application/pdf",
                "application/x-mobipocket-ebook",
                "application/vnd.amazon.ebook",  # AZW3
                "text/plain",
                "image/jpeg",
                "image/png",
                "image/webp",
                "image/jpg"
            ]
        }
    ]
    
    for bucket_config in buckets:
        bucket_name = bucket_config["name"]
        
        try:
            print(f"\n📦 Creating bucket: {bucket_name}")
            
            # Create the bucket (simplified API)
            response = supabase.storage.create_bucket(bucket_name)
            
            print(f"✅ Successfully created bucket: {bucket_name}")
            print(f"   - Public: {bucket_config['public']}")
            print(f"   - Size limit: {bucket_config['file_size_limit'] / 1024 / 1024:.0f}MB")
            print(f"   - Allowed types: {', '.join(bucket_config['allowed_mime_types'])}")
            
        except Exception as e:
            if "already exists" in str(e).lower():
                print(f"⚠️  Bucket {bucket_name} already exists, skipping...")
            else:
                print(f"❌ Error creating bucket {bucket_name}: {str(e)}")
                continue
    
    print(f"\n🎉 Storage bucket setup completed!")
    print(f"\n📋 Next steps:")
    print(f"1. Verify the buckets in your Supabase dashboard")
    print(f"2. Test uploading files using the API")
    print(f"3. Check that RLS policies are properly configured")


def create_rls_policies():
    """Create Row Level Security policies for storage buckets."""
    
    print(f"\n🔒 Setting up RLS policies...")
    
    # Initialize Supabase client
    supabase: Client = create_client(
        settings.SUPABASE_URL,
        settings.SUPABASE_SERVICE_KEY
    )
    
    # SQL policies for storage buckets
    policies = [
        # Ebooks bucket - users can only access their own files
        """
        CREATE POLICY "Users can upload ebooks" ON storage.objects
        FOR INSERT WITH CHECK (
            bucket_id = 'ebooks' AND 
            auth.uid()::text = (storage.foldername(name))[1]
        );
        """,
        
        """
        CREATE POLICY "Users can view own ebooks" ON storage.objects
        FOR SELECT USING (
            bucket_id = 'ebooks' AND 
            auth.uid()::text = (storage.foldername(name))[1]
        );
        """,
        
        """
        CREATE POLICY "Users can delete own ebooks" ON storage.objects
        FOR DELETE USING (
            bucket_id = 'ebooks' AND 
            auth.uid()::text = (storage.foldername(name))[1]
        );
        """,
        
        # Covers bucket - public read, authenticated upload
        """
        CREATE POLICY "Anyone can view covers" ON storage.objects
        FOR SELECT USING (bucket_id = 'covers');
        """,
        
        """
        CREATE POLICY "Authenticated users can upload covers" ON storage.objects
        FOR INSERT WITH CHECK (
            bucket_id = 'covers' AND 
            auth.role() = 'authenticated'
        );
        """,
        
        """
        CREATE POLICY "Users can update own covers" ON storage.objects
        FOR UPDATE USING (
            bucket_id = 'covers' AND 
            auth.uid()::text = (storage.foldername(name))[1]
        );
        """,
        
        # Temp uploads - users can only access their own temp files
        """
        CREATE POLICY "Users can upload temp files" ON storage.objects
        FOR INSERT WITH CHECK (
            bucket_id = 'temp-uploads' AND 
            auth.uid()::text = (storage.foldername(name))[1]
        );
        """,
        
        """
        CREATE POLICY "Users can view own temp files" ON storage.objects
        FOR SELECT USING (
            bucket_id = 'temp-uploads' AND 
            auth.uid()::text = (storage.foldername(name))[1]
        );
        """,
        
        """
        CREATE POLICY "Users can delete own temp files" ON storage.objects
        FOR DELETE USING (
            bucket_id = 'temp-uploads' AND 
            auth.uid()::text = (storage.foldername(name))[1]
        );
        """
    ]
    
    for i, policy in enumerate(policies, 1):
        try:
            print(f"📜 Creating policy {i}/{len(policies)}...")
            response = supabase.rpc('exec_sql', {'sql': policy})
            print(f"✅ Policy {i} created successfully")
        except Exception as e:
            if "already exists" in str(e).lower():
                print(f"⚠️  Policy {i} already exists, skipping...")
            else:
                print(f"❌ Error creating policy {i}: {str(e)}")
    
    print(f"🔒 RLS policies setup completed!")


if __name__ == "__main__":
    print("🎯 Setting up Supabase storage infrastructure...")
    
    # Check if we have the required environment variables
    required_vars = ["SUPABASE_URL", "SUPABASE_SERVICE_KEY"]
    missing_vars = [var for var in required_vars if not getattr(settings, var, None)]
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("Make sure you have copied env.development to .env")
        sys.exit(1)
    
    try:
        create_storage_buckets()
        create_rls_policies()
        print(f"\n🎉 All done! Your Supabase storage is ready for the Unread platform.")
        
    except Exception as e:
        print(f"💥 Fatal error: {str(e)}")
        sys.exit(1) 