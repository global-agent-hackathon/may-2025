import prismadb from '../db';

interface CreateWorkspaceParams {
  name: string;
  emoji?: string;
  userId: string;
}

interface UpdateWorkspaceParams {
  id: string;
  name?: string;
  emoji?: string;
}

interface CreateFormParams {
  title: string;
  description?: string;
  userId: string;
  workspaceId?: string;
}

export const workspaceService = {
  // Workspace related functions
  getUserWorkspaces: async (userId: string) => {
    return await prismadb.workspace.findMany({
      where: { userId },
      orderBy: { updatedAt: 'desc' },
    });
  },

  createWorkspace: async (data: CreateWorkspaceParams) => {
    return await prismadb.workspace.create({
      data
    });
  },

  updateWorkspace: async (data: UpdateWorkspaceParams) => {
    return await prismadb.workspace.update({
      where: { id: data.id },
      data: {
        name: data.name,
        emoji: data.emoji,
      }
    });
  },

  deleteWorkspace: async (id: string) => {
    return await prismadb.workspace.delete({
      where: { id }
    });
  },

  // Forms related functions
  getWorkspaceForms: async (workspaceId: string, userId: string) => {
    return await prismadb.form.findMany({
      where: { 
        workspaceId, 
        userId,
        isDeleted: false,
      },
      orderBy: { updatedAt: 'desc' },
    });
  },

  getUserForms: async (userId: string) => {
    return await prismadb.form.findMany({
      where: { 
        userId,
        isDeleted: false,
      },
      orderBy: { updatedAt: 'desc' },
    });
  },

  createForm: async (data: CreateFormParams) => {
    return await prismadb.form.create({
      data
    });
  },

  // Favorite related functions
  getUserFavorites: async (userId: string) => {
    const favorites = await prismadb.favorite.findMany({
      where: { userId },
      orderBy: { createdAt: 'desc' },
    });

    // Get the form details for each favorite
    const formIds = favorites.map((fav: { formId: string }) => fav.formId);
    const forms = await prismadb.form.findMany({
      where: { 
        id: { in: formIds },
        isDeleted: false
      },
      select: {
        id: true,
        title: true,
      }
    });

    // Combine the data
    return favorites.map((favorite: { formId: string, [key: string]: any }) => {
      const form = forms.find((f: { id: string }) => f.id === favorite.formId);
      return {
        ...favorite,
        form
      };
    });
  },

  toggleFavorite: async (userId: string, formId: string) => {
    const exists = await prismadb.favorite.findFirst({
      where: { userId, formId }
    });

    if (exists) {
      // Remove from favorites
      return await prismadb.favorite.delete({
        where: { id: exists.id }
      });
    } else {
      // Add to favorites
      return await prismadb.favorite.create({
        data: { userId, formId }
      });
    }
  },

  // Trash related functions
  moveToTrash: async (formId: string) => {
    return await prismadb.form.update({
      where: { id: formId },
      data: { isInTrash: true }
    });
  },

  restoreFromTrash: async (formId: string) => {
    return await prismadb.form.update({
      where: { id: formId },
      data: { isInTrash: false }
    });
  },

  getTrashItems: async (userId: string) => {
    return await prismadb.form.findMany({
      where: { 
        userId, 
        isInTrash: true,
        isDeleted: false
      },
      orderBy: { updatedAt: 'desc' },
    });
  },

  emptyTrash: async (userId: string) => {
    const now = new Date();
    
    return await prismadb.form.updateMany({
      where: { 
        userId, 
        isInTrash: true,
        isDeleted: false
      },
      data: { 
        isDeleted: true,
        deletedAt: now
      }
    });
  }
}; 