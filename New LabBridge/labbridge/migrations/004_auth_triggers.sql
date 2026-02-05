-- Migration: 004_auth_triggers.sql
-- Description: Creates triggers for automatic profile and tenant creation on user signup.
-- Run this in your Supabase SQL Editor after running the previous migrations.

-- ============================================================================
-- 1. FUNCTION: Handle new user signup
-- ============================================================================

CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
DECLARE
    new_tenant_id UUID;
    lab_name TEXT;
    user_full_name TEXT;
    user_role TEXT;
BEGIN
    -- Extract metadata from the signup
    lab_name := COALESCE(NEW.raw_user_meta_data->>'lab_name', 'Meu Laboratorio');
    user_full_name := COALESCE(NEW.raw_user_meta_data->>'full_name', split_part(NEW.email, '@', 1));
    user_role := COALESCE(NEW.raw_user_meta_data->>'role', 'owner');

    -- Create a new tenant for the user (each signup creates their own lab)
    INSERT INTO public.tenants (name, email, plan_type, subscription_status)
    VALUES (lab_name, NEW.email, 'starter', 'active')
    RETURNING id INTO new_tenant_id;

    -- Create the user profile linked to the tenant
    INSERT INTO public.profiles (id, email, full_name, tenant_id, role)
    VALUES (NEW.id, NEW.email, user_full_name, new_tenant_id, user_role);

    -- Create initial subscription for the tenant (starter plan, free)
    INSERT INTO public.subscriptions (tenant_id, plan_id, status, current_period_start, current_period_end)
    VALUES (
        new_tenant_id,
        'starter',
        'active',
        NOW(),
        NOW() + INTERVAL '1 year'
    );

    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ============================================================================
-- 2. TRIGGER: Execute after new user signup
-- ============================================================================

-- Drop existing trigger if exists
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;

-- Create trigger
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- ============================================================================
-- 3. FUNCTION: Handle user profile updates
-- ============================================================================

CREATE OR REPLACE FUNCTION public.handle_user_update()
RETURNS TRIGGER AS $$
BEGIN
    -- Sync email changes to profile
    IF OLD.email IS DISTINCT FROM NEW.email THEN
        UPDATE public.profiles
        SET email = NEW.email, updated_at = NOW()
        WHERE id = NEW.id;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ============================================================================
-- 4. TRIGGER: Execute after user update
-- ============================================================================

DROP TRIGGER IF EXISTS on_auth_user_updated ON auth.users;

CREATE TRIGGER on_auth_user_updated
    AFTER UPDATE ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_user_update();

-- ============================================================================
-- 5. FUNCTION: Handle user deletion
-- ============================================================================

CREATE OR REPLACE FUNCTION public.handle_user_delete()
RETURNS TRIGGER AS $$
BEGIN
    -- Profile will be deleted automatically due to CASCADE
    -- But we might want to handle tenant deletion if it's the only user

    -- Check if this was the only user in the tenant
    IF NOT EXISTS (
        SELECT 1 FROM public.profiles
        WHERE tenant_id = (SELECT tenant_id FROM public.profiles WHERE id = OLD.id)
        AND id != OLD.id
    ) THEN
        -- Delete the tenant if no other users
        DELETE FROM public.tenants
        WHERE id = (SELECT tenant_id FROM public.profiles WHERE id = OLD.id);
    END IF;

    RETURN OLD;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ============================================================================
-- 6. TRIGGER: Execute before user deletion
-- ============================================================================

DROP TRIGGER IF EXISTS on_auth_user_deleted ON auth.users;

CREATE TRIGGER on_auth_user_deleted
    BEFORE DELETE ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_user_delete();

-- ============================================================================
-- 7. RLS POLICIES UPDATE - Allow users to insert their own profile
-- ============================================================================

-- Drop existing policies if they exist
DROP POLICY IF EXISTS "Users can insert own profile" ON public.profiles;
DROP POLICY IF EXISTS "Service role can manage profiles" ON public.profiles;
DROP POLICY IF EXISTS "Service role can manage tenants" ON public.tenants;

-- Allow the trigger function to create profiles (runs as SECURITY DEFINER)
-- No additional policy needed as the function runs with elevated privileges

-- Allow users to read and update their own profile
CREATE POLICY "Users can read own profile" ON public.profiles
    FOR SELECT USING (id = auth.uid());

CREATE POLICY "Users can update own profile" ON public.profiles
    FOR UPDATE USING (id = auth.uid());

-- ============================================================================
-- 8. HELPER FUNCTION: Add team member to existing tenant
-- ============================================================================

CREATE OR REPLACE FUNCTION public.add_team_member(
    p_email TEXT,
    p_password TEXT,
    p_full_name TEXT,
    p_tenant_id UUID,
    p_role TEXT DEFAULT 'member'
)
RETURNS UUID AS $$
DECLARE
    new_user_id UUID;
BEGIN
    -- This function should be called by an admin to add users to their tenant
    -- Instead of creating their own tenant

    -- Note: In production, you'd use Supabase's invite flow or admin API
    -- This is a simplified version for demonstration

    RETURN new_user_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ============================================================================
-- 9. GRANT PERMISSIONS
-- ============================================================================

-- Grant execute permission on functions to authenticated users
GRANT EXECUTE ON FUNCTION public.handle_new_user() TO service_role;
GRANT EXECUTE ON FUNCTION public.handle_user_update() TO service_role;
GRANT EXECUTE ON FUNCTION public.handle_user_delete() TO service_role;

-- ============================================================================
-- END OF MIGRATION
-- ============================================================================
