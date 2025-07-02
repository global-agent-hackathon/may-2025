import { currentUser } from "@clerk/nextjs/server";
import prismadb from '../db';

interface EmailAddress {
  id: string;
  emailAddress: string;
}

export const getCurrentUserData = async () => {
  try {
    // Get the current Clerk user
    const user = await currentUser();
    
    if (!user) {
      return null;
    }

    // Check if we already have this user in our database
    const dbUser = await prismadb.user.findUnique({
      where: { externalId: user.id },
    });

    // If not, create a new user record
    if (!dbUser) {
      const primaryEmail = user.emailAddresses.find(
        (email: EmailAddress) => email.id === user.primaryEmailAddressId
      )?.emailAddress;

      if (!primaryEmail) {
        throw new Error("User doesn't have a primary email address");
      }

      const newUser = await prismadb.user.create({
        data: {
          externalId: user.id,
          email: primaryEmail,
          name: user.firstName && user.lastName 
            ? `${user.firstName} ${user.lastName}` 
            : user.username || '',
          imageUrl: user.imageUrl,
        }
      });

      return newUser;
    }

    // Update the user record if needed
    if (
      user.imageUrl !== dbUser.imageUrl ||
      (user.firstName && user.lastName && `${user.firstName} ${user.lastName}` !== dbUser.name) ||
      (user.username && !dbUser.name)
    ) {
      const updatedUser = await prismadb.user.update({
        where: { id: dbUser.id },
        data: {
          name: user.firstName && user.lastName 
            ? `${user.firstName} ${user.lastName}` 
            : user.username || dbUser.name,
          imageUrl: user.imageUrl,
        }
      });

      return updatedUser;
    }

    return dbUser;
  } catch (error) {
    console.error('Error getting current user data:', error);
    throw error;
  }
}; 