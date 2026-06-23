from typing import Any


def save_profile_to_supabase(
    supabase_client,
    user_id: str,
    student_profile: dict[str, Any],
) -> dict[str, Any]:
    """Create or update the authenticated user's single profile."""
    if not user_id:
        raise ValueError("A user_id is required.")

    if not isinstance(student_profile, dict):
        raise ValueError("student_profile must be a dictionary.")

    response = (
        supabase_client
        .table("profiles")
        .upsert(
            {
                "user_id": user_id,
                "profile_data": student_profile,
            },
            on_conflict="user_id",
        )
        .execute()
    )

    if not response.data:
        raise RuntimeError("Supabase did not return the saved profile.")

    return response.data[0]


def load_profile_from_supabase(
    supabase_client,
    user_id: str,
) -> dict[str, Any] | None:
    if not user_id:
        raise ValueError("A user_id is required.")

    response = (
        supabase_client
        .table("profiles")
        .select("*")
        .eq("user_id", user_id)
        .limit(1)
        .execute()
    )

    if not response.data:
        return None

    return response.data[0]
