import { redirect } from "next/navigation";
import { auth } from "@clerk/nextjs/server";
import prisma from "@/lib/db";
import { SubmissionViewer } from "@/components/features/submissions/submission-viewer";
import { ChatSection } from "@/components/features/chat/chat-section";

interface SubmissionPageProps {
  params: Promise<{
    id: string;
    submissionId: string;
  }>;
}

async function getFormSubmission(formId: string, submissionId: string, userId: string) {
  try {
    // Verify the form belongs to the user
    const form = await prisma.form.findUnique({
      where: {
        id: formId,
        userId,
      },
    });

    if (!form) {
      return null;
    }

    // Get form submission
    const submission = await prisma.formResponse.findUnique({
      where: {
        id: submissionId,
        formId,
      },
      include: {
        form: {
          select: {
            id: true,
            title: true,
            schema: true,
            chatThreads: {
              where: {
                userId,
              },
              orderBy: {
                updatedAt: "desc",
              },
            },
          },
        },
      },
    });

    return submission;
  } catch (error) {
    console.error("Error fetching submission:", error);
    return null;
  }
}

export default async function SubmissionPage({ params }: SubmissionPageProps) {
  const { userId } = await auth();
  if (!userId) {
    redirect("/auth/sign-in");
  }

  const { id: formId, submissionId } = await params;
  const submission = await getFormSubmission(formId, submissionId, userId);

  if (!submission) {
    redirect(`/dashboard/forms/${formId}/submissions`);
  }

  return (
    <div className="container mx-auto py-6 space-y-6">
      <h1 className="text-2xl font-bold">
        {submission.form.title} - Submission
      </h1>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Submission data */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6 space-y-4 h-fit">
          <h2 className="text-xl font-semibold">Submission Data</h2>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Submitted on {new Date(submission.createdAt).toLocaleString()}
          </p>
          <SubmissionViewer 
            data={submission.data} 
            schema={submission.form.schema} 
          />
        </div>
        
        {/* Chat section */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6 h-[600px] flex flex-col">
          <ChatSection 
            formId={submission.form.id} 
            existingThreads={submission.form.chatThreads} 
          />
        </div>
      </div>
    </div>
  );
} 