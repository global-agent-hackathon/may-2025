import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import {
  CalendarDays,
  Clock,
  DollarSign,
  Globe,
  HotelIcon,
  Info,
  Landmark,
  MapPin,
  Moon,
  Paperclip,
  Plane,
  Star,
  Sun,
  Wifi,
  Users,
  Heart,
  Home,
} from "lucide-react";
import Link from "next/link";
import { PrismaClient } from "@/lib/generated/prisma";
import { format } from "date-fns";

// Initialize Prisma Client as a singleton
const prisma = new PrismaClient();

// Type Definitions
interface DayPlan {
  day: number;
  date: string;
  morning: string;
  afternoon: string;
  evening: string;
  notes?: string;
}

interface Hotel {
  hotel_name: string;
  price: string;
  rating: string;
  address: string;
  amenities: string[];
  description?: string;
  url?: string;
}

interface Attraction {
  name: string;
  description?: string;
}

interface Flight {
  duration: string;
  price: string;
  departure_time: string;
  arrival_time: string;
  airline: string;
  flight_number?: string;
  url?: string;
  stops?: number;
}

interface Itinerary {
  day_by_day_plan: DayPlan[];
  hotels: Hotel[];
  attractions: Attraction[];
  flights: Flight[];
}

interface TripDetails {
  id: string;
  name?: string;
  status: "pending" | "completed" | "failed" | "in-progress";
  itinerary?: Itinerary;
  // Input details
  destination?: string;
  startingLocation?: string;
  travelDatesStart?: string;
  travelDatesEnd?: string;
  dateInputType?: string;
  duration?: number;
  travelingWith?: string;
  adults?: number;
  children?: number;
  ageGroups?: string[];
  budget?: number;
  budgetCurrency?: string;
  travelStyle?: string;
  budgetFlexible?: boolean;
  vibes?: string[];
  priorities?: string[];
  interests?: string;
  rooms?: number;
  pace?: number[];
  beenThereBefore?: string;
  lovedPlaces?: string;
  additionalInfo?: string;
}

// Helper functions
const formatCurrency = (amount?: number, currency?: string) => {
  if (!amount) return "Not specified";
  const symbols: Record<string, string> = {
    USD: "$",
    EUR: "€",
    GBP: "£",
    INR: "₹",
    JPY: "¥",
  };
  return `${symbols[currency || "USD"] || "$"}${amount.toLocaleString()}`;
};

const formatDate = (dateString?: string, inputType?: string) => {
  if (!dateString || inputType === "text") {
    return dateString || "Flexible dates";
  }
  try {
    return format(new Date(dateString), "MMM dd, yyyy");
  } catch {
    return dateString;
  }
};

const getPaceDescription = (pace?: number[]) => {
  if (!pace || !pace.length) return "Balanced";
  const paceValue = pace[0] || 3;
  const descriptions = {
    1: "Very relaxed",
    2: "Mostly relaxed",
    3: "Balanced",
    4: "Quite busy",
    5: "Action-packed",
  };
  return descriptions[paceValue as keyof typeof descriptions] || "Balanced";
};

// Update getTripDetails to use the singleton prisma instance
async function getTripDetails(tripId: string): Promise<TripDetails | null> {
  try {
    const tripPlan = await prisma.tripPlan.findUnique({
      where: { id: tripId },
      include: {
        status: true,
        output: true,
      },
    });

    if (!tripPlan) {
      return null;
    }

    // Map the database status to our TripDetails status
    let status: TripDetails["status"] = "pending";
    if (tripPlan.status) {
      switch (tripPlan.status.status) {
        case "completed":
          status = "completed";
          break;
        case "processing":
          status = "in-progress";
          break;
        case "failed":
          status = "failed";
          break;
        default:
          status = "pending";
      }
    }

    // Parse the itinerary JSON if it exists
    let itinerary: Itinerary | undefined;
    if (tripPlan.output?.itinerary) {
      try {
        itinerary = JSON.parse(tripPlan.output.itinerary) as Itinerary;
      } catch (e) {
        console.error("Failed to parse itinerary JSON:", e);
      }
    }

    return {
      id: tripPlan.id,
      name: tripPlan.name,
      status,
      itinerary,
      // Input details
      destination: tripPlan.destination,
      startingLocation: tripPlan.startingLocation,
      travelDatesStart: tripPlan.travelDatesStart
        ? String(tripPlan.travelDatesStart)
        : undefined,
      travelDatesEnd: tripPlan.travelDatesEnd
        ? String(tripPlan.travelDatesEnd)
        : undefined,
      dateInputType: tripPlan.dateInputType,
      duration: tripPlan.duration ?? undefined,
      travelingWith: tripPlan.travelingWith,
      adults: tripPlan.adults,
      children: tripPlan.children,
      ageGroups: tripPlan.ageGroups as string[],
      budget: tripPlan.budget,
      budgetCurrency: tripPlan.budgetCurrency,
      travelStyle: tripPlan.travelStyle,
      budgetFlexible: tripPlan.budgetFlexible,
      vibes: tripPlan.vibes as string[],
      priorities: tripPlan.priorities as string[],
      interests: tripPlan.interests ?? undefined,
      rooms: tripPlan.rooms,
      pace: tripPlan.pace as number[],
      beenThereBefore: tripPlan.beenThereBefore ?? undefined,
      lovedPlaces: tripPlan.lovedPlaces ?? undefined,
      additionalInfo: tripPlan.additionalInfo ?? undefined,
    };
  } catch (error) {
    console.error("Error fetching trip details:", error);
    return null;
  }
}

// Helper function to render status badge
function StatusBadge({ status }: { status: TripDetails["status"] }) {
  let variant: "default" | "secondary" | "destructive" | "outline" = "default";
  let text = status.toUpperCase();

  switch (status) {
    case "completed":
      variant = "default"; // Using Tailwind's green for success
      text = "Completed";
      break;
    case "pending":
      variant = "secondary"; // Using Tailwind's yellow for pending
      text = "Pending";
      break;
    case "in-progress":
      variant = "outline"; // Using Tailwind's blue for in-progress
      text = "In Progress";
      break;
    case "failed":
      variant = "destructive";
      text = "Failed";
      break;
  }
  return (
    <Badge
      variant={variant}
      className={
        status === "completed"
          ? "bg-green-500 hover:bg-green-600 text-white"
          : status === "pending"
          ? "bg-yellow-500 hover:bg-yellow-600 text-black"
          : status === "in-progress"
          ? "bg-blue-500 hover:bg-blue-600 text-white"
          : ""
      }
    >
      {text}
    </Badge>
  );
}

export default async function TripDetailsPage({
  params,
}: {
  params: { id: string };
}) {
  const trip = await getTripDetails(params.id);

  if (!trip) {
    return (
      <div className="container mx-auto p-4 flex flex-col items-center justify-center min-h-[calc(100vh-10rem)]">
        <Landmark size={64} className="text-muted-foreground mb-4" />
        <h1 className="text-2xl font-semibold mb-2">Trip Not Found</h1>
        <p className="text-muted-foreground text-center">
          The trip you are looking for does not exist or could not be loaded.
        </p>
        <Link href="/" className="mt-4 text-primary hover:underline">
          Go back to homepage
        </Link>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-4 md:p-8 space-y-8">
      <header className="flex flex-col space-y-2">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between">
          <div>
            {trip.destination && (
              <h1 className="text-3xl md:text-4xl font-bold tracking-tight flex items-center">
                <MapPin className="h-6 w-6 mr-2 text-primary" />
                {trip.destination}
              </h1>
            )}
            {trip.name && trip.name !== trip.destination && (
              <p className="text-xl text-muted-foreground mt-1">{trip.name}</p>
            )}
          </div>
          <StatusBadge status={trip.status} />
        </div>
      </header>

      <Separator />

      {/* Trip Input Details Section */}
      <section className="bg-muted/30 rounded-lg p-6 border border-border">
        <h2 className="text-2xl font-semibold mb-4 flex items-center">
          <Globe className="mr-3 h-6 w-6 text-primary" /> Trip Details
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {/* Destination and Location */}
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-lg flex items-center">
                <MapPin className="h-4 w-4 mr-2 text-primary" />
                Destination
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div>
                  <span className="font-medium">To:</span>{" "}
                  <span className="text-muted-foreground">
                    {trip.destination}
                  </span>
                </div>
                <div>
                  <span className="font-medium">From:</span>{" "}
                  <span className="text-muted-foreground">
                    {trip.startingLocation}
                  </span>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Dates and Duration */}
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-lg flex items-center">
                <CalendarDays className="h-4 w-4 mr-2 text-primary" />
                Travel Dates
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div>
                  <span className="font-medium">From:</span>{" "}
                  <span className="text-muted-foreground">
                    {formatDate(trip.travelDatesStart, trip.dateInputType)}
                  </span>
                </div>
                {trip.travelDatesEnd && (
                  <div>
                    <span className="font-medium">To:</span>{" "}
                    <span className="text-muted-foreground">
                      {formatDate(trip.travelDatesEnd, trip.dateInputType)}
                    </span>
                  </div>
                )}
                {trip.duration && (
                  <div>
                    <span className="font-medium">Duration:</span>{" "}
                    <span className="text-muted-foreground">
                      {trip.duration} days
                    </span>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Travelers */}
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-lg flex items-center">
                <Users className="h-4 w-4 mr-2 text-primary" />
                Travelers
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div>
                  <span className="font-medium">Type:</span>{" "}
                  <span className="text-muted-foreground">
                    {trip.travelingWith}
                  </span>
                </div>
                <div>
                  <span className="font-medium">Group:</span>{" "}
                  <span className="text-muted-foreground">
                    {trip.adults} adult{trip.adults !== 1 ? "s" : ""}
                    {trip.children && trip.children > 0
                      ? `, ${trip.children} child${
                          trip.children !== 1 ? "ren" : ""
                        }`
                      : ""}
                  </span>
                </div>
                {trip.ageGroups && trip.ageGroups.length > 0 && (
                  <div>
                    <span className="font-medium">Ages:</span>{" "}
                    <span className="text-muted-foreground">
                      {trip.ageGroups.join(", ")}
                    </span>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Accommodation */}
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-lg flex items-center">
                <Home className="h-4 w-4 mr-2 text-primary" />
                Accommodation
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div>
                  <span className="font-medium">Type:</span>{" "}
                  <span className="text-muted-foreground">
                    {trip.travelStyle}
                  </span>
                </div>
                <div>
                  <span className="font-medium">Rooms:</span>{" "}
                  <span className="text-muted-foreground">{trip.rooms}</span>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Budget */}
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-lg flex items-center">
                <DollarSign className="h-4 w-4 mr-2 text-primary" />
                Budget
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div>
                  <span className="font-medium">Amount:</span>{" "}
                  <span className="text-muted-foreground">
                    {formatCurrency(trip.budget, trip.budgetCurrency)} per
                    person
                  </span>
                </div>
                <div>
                  <span className="font-medium">Flexible:</span>{" "}
                  <span className="text-muted-foreground">
                    {trip.budgetFlexible ? "Yes" : "No"}
                  </span>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Trip Style */}
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-lg flex items-center">
                <Heart className="h-4 w-4 mr-2 text-primary" />
                Trip Style
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div>
                  <span className="font-medium">Pace:</span>{" "}
                  <span className="text-muted-foreground">
                    {getPaceDescription(trip.pace)}
                  </span>
                </div>
                {trip.vibes && trip.vibes.length > 0 && (
                  <div>
                    <span className="font-medium block mb-1">Vibes:</span>
                    <div className="flex flex-wrap gap-1">
                      {trip.vibes.map((vibe) => (
                        <Badge
                          key={vibe}
                          variant="secondary"
                          className="text-xs"
                        >
                          {vibe}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}
                {trip.priorities && trip.priorities.length > 0 && (
                  <div>
                    <span className="font-medium block mb-1">Priorities:</span>
                    <div className="flex flex-wrap gap-1">
                      {trip.priorities.map((priority) => (
                        <Badge
                          key={priority}
                          variant="outline"
                          className="text-xs"
                        >
                          {priority}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Additional Information */}
        {(trip.interests ||
          trip.beenThereBefore ||
          trip.lovedPlaces ||
          trip.additionalInfo) && (
          <div className="mt-6">
            <h3 className="text-xl font-semibold mb-3">
              Additional Information
            </h3>
            <Card>
              <CardContent className="pt-6 grid grid-cols-1 md:grid-cols-2 gap-4">
                {trip.interests && (
                  <div>
                    <h4 className="font-medium mb-1">Specific Interests:</h4>
                    <p className="text-muted-foreground text-sm">
                      {trip.interests}
                    </p>
                  </div>
                )}
                {trip.beenThereBefore && (
                  <div>
                    <h4 className="font-medium mb-1">Previous Visits:</h4>
                    <p className="text-muted-foreground text-sm">
                      {trip.beenThereBefore}
                    </p>
                  </div>
                )}
                {trip.lovedPlaces && (
                  <div>
                    <h4 className="font-medium mb-1">Loved Places:</h4>
                    <p className="text-muted-foreground text-sm">
                      {trip.lovedPlaces}
                    </p>
                  </div>
                )}
                {trip.additionalInfo && (
                  <div className="md:col-span-2">
                    <h4 className="font-medium mb-1">
                      Additional Information:
                    </h4>
                    <p className="text-muted-foreground text-sm">
                      {trip.additionalInfo}
                    </p>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        )}
      </section>

      {trip.status === "completed" && trip.itinerary ? (
        <div className="space-y-12">
          {/* Day-by-Day Plan Section */}
          <section>
            <h2 className="text-2xl font-semibold mb-6 flex items-center">
              <CalendarDays className="mr-3 h-6 w-6 text-primary" /> Daily
              Itinerary
            </h2>
            <div className="grid grid-cols-1 gap-6">
              {trip.itinerary.day_by_day_plan.map((dayPlan) => (
                <Card
                  key={dayPlan.day}
                  className="overflow-hidden border-l-4 border-l-primary"
                >
                  <CardHeader className="bg-muted/50 pb-3">
                    <div className="flex items-center justify-between">
                      <CardTitle className="text-xl flex items-center">
                        <span className="flex h-8 w-8 items-center justify-center rounded-full bg-primary text-primary-foreground mr-3">
                          {dayPlan.day}
                        </span>
                        <span>Day {dayPlan.day}</span>
                      </CardTitle>
                      {dayPlan.date && (
                        <Badge variant="outline" className="ml-auto">
                          <CalendarDays className="mr-1 h-3 w-3" />
                          {new Date(dayPlan.date).toLocaleDateString(
                            undefined,
                            { year: "numeric", month: "long", day: "numeric" }
                          )}
                        </Badge>
                      )}
                    </div>
                  </CardHeader>
                  <CardContent className="pt-6 grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div className="bg-muted/30 p-4 rounded-lg border border-border">
                      <div className="flex items-center mb-3">
                        <Sun className="h-5 w-5 mr-2 text-yellow-500" />
                        <h3 className="font-medium">Morning</h3>
                      </div>
                      <p className="text-muted-foreground">{dayPlan.morning}</p>
                    </div>
                    <div className="bg-muted/30 p-4 rounded-lg border border-border">
                      <div className="flex items-center mb-3">
                        <Sun className="h-5 w-5 mr-2 text-orange-500" />
                        <h3 className="font-medium">Afternoon</h3>
                      </div>
                      <p className="text-muted-foreground">
                        {dayPlan.afternoon}
                      </p>
                    </div>
                    <div className="bg-muted/30 p-4 rounded-lg border border-border">
                      <div className="flex items-center mb-3">
                        <Moon className="h-5 w-5 mr-2 text-indigo-500" />
                        <h3 className="font-medium">Evening</h3>
                      </div>
                      <p className="text-muted-foreground">{dayPlan.evening}</p>
                    </div>
                  </CardContent>
                  {dayPlan.notes && (
                    <div className="px-0">
                      <div className="bg-yellow-100 p-4 flex items-start">
                        <Paperclip className="h-5 w-5 mr-2 mt-0.5 text-primary flex-shrink-0" />
                        <p className="text-sm">
                          <span className="font-medium">Note:</span>{" "}
                          {dayPlan.notes}
                        </p>
                      </div>
                    </div>
                  )}
                </Card>
              ))}
            </div>
          </section>

          {/* Hotels Section */}
          {trip.itinerary.hotels && trip.itinerary.hotels.length > 0 && (
            <section>
              <h2 className="text-2xl font-semibold mb-6 flex items-center">
                <HotelIcon className="mr-3 h-6 w-6 text-primary" />{" "}
                Accommodation
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {trip.itinerary.hotels.map((hotel, index) => (
                  <Card
                    key={index}
                    className="flex flex-col border-t-4 border-t-primary"
                  >
                    <CardHeader>
                      <CardTitle className="text-xl">
                        {hotel.hotel_name}
                      </CardTitle>
                      {hotel.rating && (
                        <div className="flex items-center text-sm text-muted-foreground mt-1">
                          <Star className="h-4 w-4 mr-1 text-yellow-400 fill-yellow-400" />{" "}
                          {hotel.rating}
                        </div>
                      )}
                    </CardHeader>
                    <CardContent className="flex-grow space-y-2">
                      <p className="flex items-start">
                        <MapPin className="h-5 w-5 mr-2 mt-0.5 text-muted-foreground flex-shrink-0" />{" "}
                        {hotel.address}
                      </p>
                      {hotel.price && (
                        <p className="flex items-center">
                          <DollarSign className="h-5 w-5 mr-2 text-muted-foreground" />{" "}
                          {hotel.price}
                        </p>
                      )}
                      {hotel.description && (
                        <p className="text-sm text-muted-foreground">
                          {hotel.description}
                        </p>
                      )}
                      {hotel.amenities && hotel.amenities.length > 0 && (
                        <div>
                          <h4 className="font-medium mt-2 mb-1">Amenities:</h4>
                          <div className="flex flex-wrap gap-2">
                            {hotel.amenities.map((amenity, i) => (
                              <Badge
                                key={i}
                                variant="outline"
                                className="text-xs"
                              >
                                {amenity === "Free WiFi" && (
                                  <Wifi className="h-3 w-3 mr-1" />
                                )}
                                {amenity}
                              </Badge>
                            ))}
                          </div>
                        </div>
                      )}
                    </CardContent>
                    {hotel.url && (
                      <CardFooter className="bg-muted/30 border-t">
                        <Link
                          href={hotel.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-primary hover:underline text-sm flex items-center"
                        >
                          Visit Hotel Website{" "}
                          <Globe className="h-4 w-4 ml-1.5" />
                        </Link>
                      </CardFooter>
                    )}
                  </Card>
                ))}
              </div>
            </section>
          )}

          {/* Flights Section */}
          {trip.itinerary.flights && trip.itinerary.flights.length > 0 && (
            <section>
              <h2 className="text-2xl font-semibold mb-6 flex items-center">
                <Plane className="mr-3 h-6 w-6 text-primary" /> Flights
              </h2>
              <div className="space-y-6">
                {trip.itinerary.flights.map((flight, index) => (
                  <Card
                    key={index}
                    className="border-r-4 border-r-primary overflow-hidden"
                  >
                    <CardHeader className="bg-muted/30">
                      <CardTitle className="text-xl flex items-center">
                        <Plane className="h-5 w-5 mr-2 text-primary" />
                        {flight.airline}
                      </CardTitle>
                      {flight.flight_number && (
                        <CardDescription>
                          Flight {flight.flight_number}
                        </CardDescription>
                      )}
                    </CardHeader>
                    <CardContent className="py-6">
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm">
                        <div className="bg-muted/20 p-3 rounded-lg">
                          <p className="font-medium flex items-center">
                            <Clock className="h-4 w-4 mr-2 text-primary" />
                            Duration:
                          </p>
                          <p className="text-muted-foreground mt-1">
                            {flight.duration}
                          </p>
                        </div>
                        <div className="bg-muted/20 p-3 rounded-lg">
                          <p className="font-medium flex items-center">
                            <DollarSign className="h-4 w-4 mr-2 text-primary" />
                            Price:
                          </p>
                          <p className="text-muted-foreground mt-1">
                            {flight.price}
                          </p>
                        </div>
                        <div className="bg-muted/20 p-3 rounded-lg">
                          <p className="font-medium flex items-center">
                            <Clock className="h-4 w-4 mr-2 text-green-500" />
                            Departure:
                          </p>
                          <p className="text-muted-foreground mt-1">
                            {flight.departure_time || "Not specified"}
                          </p>
                        </div>
                        <div className="bg-muted/20 p-3 rounded-lg">
                          <p className="font-medium flex items-center">
                            <Clock className="h-4 w-4 mr-2 text-red-500" />
                            Arrival:
                          </p>
                          <p className="text-muted-foreground mt-1">
                            {flight.arrival_time || "Not specified"}
                          </p>
                        </div>
                        {typeof flight.stops !== "undefined" && (
                          <div className="bg-muted/20 p-3 rounded-lg">
                            <p className="font-medium">Stops:</p>
                            <p className="text-muted-foreground mt-1">
                              {flight.stops}
                            </p>
                          </div>
                        )}
                      </div>
                    </CardContent>
                    {flight.url && (
                      <CardFooter className="bg-muted/30 border-t">
                        <Link
                          href={flight.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-primary hover:underline text-sm flex items-center"
                        >
                          Book / View Flight{" "}
                          <Globe className="h-4 w-4 ml-1.5" />
                        </Link>
                      </CardFooter>
                    )}
                  </Card>
                ))}
              </div>
            </section>
          )}

          {/* Attractions Section */}
          {trip.itinerary.attractions &&
            trip.itinerary.attractions.length > 0 && (
              <section>
                <h2 className="text-2xl font-semibold mb-6 flex items-center">
                  <Landmark className="mr-3 h-6 w-6 text-primary" /> Attractions
                  & Activities
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {trip.itinerary.attractions.map((attraction, index) => (
                    <Card
                      key={index}
                      className="group hover:shadow-md transition-all duration-300 border-b-4 border-b-transparent hover:border-b-primary"
                    >
                      <CardHeader>
                        <CardTitle className="text-lg group-hover:text-primary transition-colors">
                          {attraction.name}
                        </CardTitle>
                      </CardHeader>
                      {attraction.description && (
                        <CardContent>
                          <p className="text-sm text-muted-foreground">
                            {attraction.description}
                          </p>
                        </CardContent>
                      )}
                    </Card>
                  ))}
                </div>
              </section>
            )}
        </div>
      ) : (
        <div className="text-center py-10">
          <Info size={48} className="text-muted-foreground mx-auto mb-4" />
          <h2 className="text-xl font-semibold mb-2">
            {trip.status === "pending" && "Trip Plan in Progress"}
            {trip.status === "in-progress" && "Trip Plan is Being Generated"}
            {trip.status === "failed" && "Failed to Generate Trip Plan"}
            {trip.status !== "pending" &&
              trip.status !== "in-progress" &&
              trip.status !== "failed" &&
              trip.status !== "completed" &&
              "Trip Details Unavailable"}
          </h2>
          <p className="text-muted-foreground">
            {trip.status === "pending" &&
              "Your trip itinerary is currently being planned. Please check back later."}
            {trip.status === "in-progress" &&
              "We are working on your trip details. This might take a few moments."}
            {trip.status === "failed" &&
              "Something went wrong while generating your trip plan. Please try again or contact support."}
            {trip.status !== "pending" &&
              trip.status !== "in-progress" &&
              trip.status !== "failed" &&
              trip.status !== "completed" &&
              "The details for this trip are not available in its current state."}
          </p>
        </div>
      )}
    </div>
  );
}
