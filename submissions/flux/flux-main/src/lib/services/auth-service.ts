import prismadb from '../db';

export const authService = {
  getUserById: async (userId: string) => {
    return await prismadb.user.findUnique({
      where: { id: userId },
    });
  },

  getUserByExternalId: async (externalId: string) => {
    return await prismadb.user.findUnique({
      where: { externalId },
    });
  },

  // Check if user has access to a workspace with more strict query
  verifyWorkspaceAccess: async (workspaceId: string, userId: string): Promise<boolean> => {
    if (!workspaceId || !userId) return false;
    
    const workspace = await prismadb.workspace.findFirst({
      where: { 
        id: workspaceId,
        userId: userId
      },
    });
    
    return !!workspace;
  },

  // Check if user has access to a form with more strict query
  verifyFormAccess: async (formId: string, userId: string): Promise<boolean> => {
    if (!formId || !userId) return false;
    
    const form = await prismadb.form.findFirst({
      where: { 
        id: formId,
        userId: userId
      },
    });
    
    return !!form;
  },

  // Check if form is published (for public access)
  isFormPublished: async (formId: string): Promise<boolean> => {
    if (!formId) return false;
    
    const form = await prismadb.form.findUnique({
      where: { id: formId },
      select: { published: true }
    });
    
    return !!form?.published;
  }
}; 