import { NextRequest, NextResponse } from 'next/server';
import { prisma } from '@/lib/prisma';

interface TripFormData {
  name: string;
  destination: string;
  startingLocation: string;
  travelDates: { start: string; end: string };
  dateInputType: "picker" | "text";
  duration: number;
  travelingWith: string;
  adults: number;
  children: number;
  ageGroups: string[];
  budget: number;
  budgetCurrency: string;
  travelStyle: string;
  budgetFlexible: boolean;
  vibes: string[];
  priorities: string[];
  interests?: string;
  rooms: number;
  pace: number[];
  beenThereBefore?: string;
  lovedPlaces?: string;
  additionalInfo?: string;
}

export async function POST(request: NextRequest) {
  try {
    const tripData: TripFormData = await request.json();

    // Log the trip data for debugging
    console.log('Received trip planning data:', JSON.stringify(tripData, null, 2));

    // Validate required fields
    if (!tripData.name || !tripData.destination || !tripData.startingLocation) {
      return NextResponse.json(
        {
          success: false,
          message: 'Missing required fields: name, destination, or starting location'
        },
        { status: 400 }
      );
    }

    // Save to database
    const savedTripPlan = await prisma.tripPlan.create({
      data: {
        name: tripData.name,
        destination: tripData.destination,
        startingLocation: tripData.startingLocation,
        travelDatesStart: tripData.travelDates.start,
        travelDatesEnd: tripData.travelDates.end || null,
        dateInputType: tripData.dateInputType || "picker",
        duration: tripData.duration || null,
        travelingWith: tripData.travelingWith,
        adults: tripData.adults || 1,
        children: tripData.children || 0,
        ageGroups: tripData.ageGroups || [],
        budget: tripData.budget,
        budgetCurrency: tripData.budgetCurrency || "USD",
        travelStyle: tripData.travelStyle,
        budgetFlexible: tripData.budgetFlexible || false,
        vibes: tripData.vibes || [],
        priorities: tripData.priorities || [],
        interests: tripData.interests || null,
        rooms: tripData.rooms || 1,
        pace: tripData.pace || [3],
        beenThereBefore: tripData.beenThereBefore || null,
        lovedPlaces: tripData.lovedPlaces || null,
        additionalInfo: tripData.additionalInfo || null,
        // userId can be added later when auth is implemented
        userId: null
      }
    });

    console.log('Trip plan saved to database:', savedTripPlan.id);

    return NextResponse.json(
      {
        success: true,
        message: 'Trip plan saved successfully!',
        tripId: savedTripPlan.id,
        tripPlan: savedTripPlan
      },
      { status: 200 }
    );
  } catch (error) {
    console.error('Error processing trip submission:', error);
    return NextResponse.json(
      {
        success: false,
        message: 'Failed to save trip plan to database'
      },
      { status: 500 }
    );
  }
}