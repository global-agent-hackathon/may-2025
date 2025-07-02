import { PrismaClient } from '../src/generated/prisma'

const prisma = new PrismaClient()

async function main() {
  console.log('Starting seeding...')

  // Create a test user
  const user = await prisma.user.upsert({
    where: { email: 'test@example.com' },
    update: {},
    create: {
      id: 'user_1',
      externalId: 'clerk_user_1',
      email: 'test@example.com',
      name: 'Test User',
      imageUrl: 'https://api.dicebear.com/7.x/avataaars/svg?seed=user',
    },
  })

  console.log('Created user:', user.id)

  // Create some workspaces
  const workspace1 = await prisma.workspace.upsert({
    where: { id: 'workspace_1' },
    update: {},
    create: {
      id: 'workspace_1',
      name: 'Work Projects',
      emoji: '💼',
      userId: user.id,
    },
  })

  const workspace2 = await prisma.workspace.upsert({
    where: { id: 'workspace_2' },
    update: {},
    create: {
      id: 'workspace_2',
      name: 'Personal',
      emoji: '🏠',
      userId: user.id,
    },
  })

  console.log('Created workspaces:', workspace1.id, workspace2.id)

  // Create some forms
  const form1 = await prisma.form.upsert({
    where: { id: 'form_1' },
    update: {},
    create: {
      id: 'form_1',
      title: 'Job Application Form',
      description: 'Application form for job candidates',
      schema: {
        fields: [
          {
            id: 'field_1',
            type: 'text',
            label: 'Full Name',
            required: true,
            placeholder: 'Enter your full name'
          },
          {
            id: 'field_2',
            type: 'email',
            label: 'Email Address',
            required: true,
            placeholder: 'Enter your email address'
          }
        ]
      },
      published: true,
      userId: user.id,
      workspaceId: workspace1.id,
    },
  })

  const form2 = await prisma.form.upsert({
    where: { id: 'form_2' },
    update: {},
    create: {
      id: 'form_2',
      title: 'Customer Feedback',
      description: 'Gather feedback from customers',
      schema: {
        fields: [
          {
            id: 'field_1',
            type: 'text',
            label: 'What did you like about our service?',
            required: false,
            placeholder: 'Please share your feedback'
          },
          {
            id: 'field_2',
            type: 'number',
            label: 'Rating (1-5)',
            required: true,
            placeholder: 'Rate our service'
          }
        ]
      },
      published: false,
      userId: user.id,
      workspaceId: workspace2.id,
    },
  })

  console.log('Created forms:', form1.id, form2.id)

  // Create a favorite
  const favorite = await prisma.favorite.upsert({
    where: { 
      userId_formId: {
        userId: user.id,
        formId: form1.id,
      }
    },
    update: {},
    create: {
      userId: user.id,
      formId: form1.id,
    },
  })

  console.log('Created favorite:', favorite.id)

  console.log('Seeding completed.')
}

main()
  .catch((e) => {
    console.error(e)
    process.exit(1)
  })
  .finally(async () => {
    await prisma.$disconnect()
  }) 