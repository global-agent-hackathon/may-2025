import { NextRequest, NextResponse } from 'next/server'
import prismadb from '@/lib/db'
import { formResponseSchema } from '@/schemas/form'
import { getAuth } from '@clerk/nextjs/server'

// This endpoint is dynamic and will be server-rendered
export const dynamic = 'force-dynamic';

// Get responses for a specific form
export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
): Promise<NextResponse> {
  try {
    const { id } = await params
    
    if (!id) {
      return new NextResponse(JSON.stringify({ error: 'Form ID is required' }), {
        status: 400,
      })
    }
    
    const responses = await prismadb.formResponse.findMany({
      where: { formId: id },
      orderBy: { createdAt: 'desc' },
    })
    
    return NextResponse.json(responses)
  } catch (error) {
    console.error('Error fetching form responses:', error)
    return new NextResponse(JSON.stringify({ error: 'Internal Server Error' }), {
      status: 500,
    })
  }
}

// Submit a new response for a form
export async function POST(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
): Promise<NextResponse> {
  try {
    const { id } = await params;
    console.log('POST request received for form response', id);
    
    // Validate form ID
    if (!id) {
      console.error('Form ID is missing');
      return NextResponse.json({ error: 'Form ID is required' }, { status: 400 })
    }
    
    // Check if form exists and is published
    const form = await prismadb.form.findUnique({
      where: { id: id },
    })
    
    if (!form) {
      console.error(`Form with ID ${id} not found`);
      return NextResponse.json({ error: `Form with ID ${id} not found` }, { status: 404 })
    }
    
    if (!form.published) {
      console.error(`Form with ID ${id} is not published`);
      return NextResponse.json(
        { error: 'This form is not accepting responses' },
        { status: 403 }
      )
    }
    
    // Get the form data
    const formResponseData = await request.json()
    
    console.log('Received form submission data:', JSON.stringify(formResponseData).substring(0, 200) + '...');
    
    // Validate response data with Zod
    try {
      formResponseSchema.parse(formResponseData);
    } catch (validationError) {
      console.error('Form response validation error:', validationError);
      return NextResponse.json({ 
        error: 'Invalid form response data', 
        details: validationError 
      }, { status: 400 });
    }
    
    try {
      // Create the response
      const response = await prismadb.formResponse.create({
        data: {
          formId: id,
          data: formResponseData as any,
        },
      });
      
      console.log('Form response created successfully:', response.id);
      return NextResponse.json({ 
        success: true, 
        responseId: response.id,
        message: 'Form response submitted successfully'
      });
    } catch (dbError) {
      console.error('Database error creating form response:', dbError);
      return NextResponse.json({ 
        error: 'Database error', 
        message: dbError instanceof Error ? dbError.message : String(dbError)
      }, { status: 500 });
    }
  } catch (error) {
    console.error('Error creating form response:', error)
    return NextResponse.json(
      { error: 'Failed to submit form response', message: error instanceof Error ? error.message : String(error) },
      { status: 500 }
    )
  }
}

// Remove the deprecated export const config
// export const config = {
//   matcher: ['/api/forms/:id/responses'],
// }; 
