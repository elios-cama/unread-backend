-- Enable Row Level Security for all tables
-- Run this in your Supabase SQL Editor

-- Enable RLS on users table
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- Enable RLS on ebooks table
ALTER TABLE ebooks ENABLE ROW LEVEL SECURITY;

-- Enable RLS on collections table
ALTER TABLE collections ENABLE ROW LEVEL SECURITY;

-- Enable RLS on collection_items table
ALTER TABLE collection_items ENABLE ROW LEVEL SECURITY;

-- Enable RLS on reading_progress table
ALTER TABLE reading_progress ENABLE ROW LEVEL SECURITY;

-- Enable RLS on reviews table
ALTER TABLE reviews ENABLE ROW LEVEL SECURITY;

-- Enable RLS on share_links table
ALTER TABLE share_links ENABLE ROW LEVEL SECURITY;

-- Basic RLS policies (you can customize these later)

-- Users can read their own profile
CREATE POLICY "Users can view own profile" ON users
    FOR SELECT USING (auth.uid() = id::text);

-- Users can update their own profile
CREATE POLICY "Users can update own profile" ON users
    FOR UPDATE USING (auth.uid() = id::text);

-- Authors can manage their own ebooks
CREATE POLICY "Authors can manage own ebooks" ON ebooks
    FOR ALL USING (auth.uid() = author_id::text);

-- Everyone can read published ebooks
CREATE POLICY "Anyone can view published ebooks" ON ebooks
    FOR SELECT USING (status = 'published');

-- Authors can manage their own collections
CREATE POLICY "Authors can manage own collections" ON collections
    FOR ALL USING (auth.uid() = author_id::text);

-- Users can manage their own reading progress
CREATE POLICY "Users can manage own reading progress" ON reading_progress
    FOR ALL USING (auth.uid() = user_id::text);

-- Users can manage their own reviews
CREATE POLICY "Users can manage own reviews" ON reviews
    FOR ALL USING (auth.uid() = user_id::text);

-- Everyone can read reviews
CREATE POLICY "Anyone can read reviews" ON reviews
    FOR SELECT USING (true);

-- Share links are publicly readable
CREATE POLICY "Anyone can read share links" ON share_links
    FOR SELECT USING (true);

-- Authors can manage their own share links
CREATE POLICY "Authors can manage own share links" ON share_links
    FOR ALL USING (auth.uid() = (SELECT author_id::text FROM ebooks WHERE id = ebook_id)); 