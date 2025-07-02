import prismadb from "@/lib/prismadb";

/**
 * Gets the database user ID from the Clerk user ID
 * @param clerkUserId - The Clerk user ID
 * @returns The database user ID or null if not found
 */
export async function getDbUserId(clerkUserId: string): Promise<string | null> {
  try {
    console.log("[AUTH_SERVICE] Looking up DB user ID for Clerk ID:", clerkUserId);
    
    const user = await prismadb.user.findUnique({
      where: {
        externalId: clerkUserId,
      },
      select: {
        id: true,
      },
    });

    if (user?.id) {
      console.log("[AUTH_SERVICE] Found DB user ID:", user.id);
      return user.id;
    } else {
      console.warn("[AUTH_SERVICE] No database user found for Clerk ID:", clerkUserId);
      return null;
    }
  } catch (error) {
    console.error("[AUTH_SERVICE] Error getting DB user ID:", error);
    return null;
  }
}

/**
 * Verifies a user's access to a workspace
 * @param workspaceId - The workspace ID
 * @param userId - The database user ID
 * @returns Boolean indicating whether the user has access
 */
export async function verifyWorkspaceAccess(
  workspaceId: string,
  userId: string
): Promise<boolean> {
  try {
    const workspace = await prismadb.workspace.findUnique({
      where: {
        id: workspaceId,
        userId,
      },
    });

    return !!workspace;
  } catch (error) {
    console.error("Error verifying workspace access:", error);
    return false;
  }
}

// Export as a service object for easier mocking in tests
const authService = {
  getDbUserId,
  verifyWorkspaceAccess,
};

export default authService; 