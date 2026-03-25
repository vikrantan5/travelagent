import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';

interface TripData {
  destination?: string;
  startingLocation?: string;
  travelDatesStart?: string;
  travelDatesEnd?: string;
  duration?: number;
  adults?: number;
  children?: number;
  budget?: number;
  budgetCurrency?: string;
  itinerary?: any;
  budget_agent_response?: string;
  destination_agent_response?: string;
  images?: Array<{ place: string; image_url: string }>;
  product_recommendations?: Array<{ name: string; why_needed?: string; reason?: string }>;
  products?: Array<{ name: string; why_needed?: string; reason?: string }>;
}

export async function generateTripPDF(trip: TripData) {
  const doc = new jsPDF();
  let yPosition = 20;
  const pageWidth = doc.internal.pageSize.getWidth();
  const margin = 20;
  const contentWidth = pageWidth - 2 * margin;

  // Helper function to add text with word wrap
  const addText = (text: string, fontSize: number = 10, isBold: boolean = false, color: [number, number, number] = [0, 0, 0]) => {
    doc.setFontSize(fontSize);
    doc.setFont('helvetica', isBold ? 'bold' : 'normal');
    doc.setTextColor(color[0], color[1], color[2]);
    const lines = doc.splitTextToSize(text, contentWidth);
    
    lines.forEach((line: string) => {
      if (yPosition > 280) {
        doc.addPage();
        yPosition = 20;
      }
      doc.text(line, margin, yPosition);
      yPosition += fontSize * 0.5;
    });
    yPosition += 5;
  };

  // Add header with gradient effect simulation
  doc.setFillColor(147, 51, 234); // Purple
  doc.rect(0, 0, pageWidth, 40, 'F');
  doc.setTextColor(255, 255, 255);
  doc.setFontSize(24);
  doc.setFont('helvetica', 'bold');
  doc.text('Travelethic ', pageWidth / 2, 25, { align: 'center' });
  doc.setFontSize(12);
  doc.text('Your Personalized Travel Itinerary', pageWidth / 2, 33, { align: 'center' });
  
  yPosition = 50;
  doc.setTextColor(0, 0, 0);

  // Trip Overview
  addText(`Trip to ${trip.destination || 'Unknown'}`, 18, true, [147, 51, 234]);
  
  if (trip.startingLocation) {
    addText(`From: ${trip.startingLocation}`, 11);
  }
  
  if (trip.travelDatesStart) {
    addText(`Dates: ${trip.travelDatesStart} to ${trip.travelDatesEnd || 'TBD'}`, 11);
  }
  
  if (trip.duration) {
    addText(`Duration: ${trip.duration} days`, 11);
  }
  
  if (trip.adults || trip.children) {
    addText(`Travelers: ${trip.adults || 0} Adult(s)${trip.children ? `, ${trip.children} Child(ren)` : ''}`, 11);
  }
  
  if (trip.budget) {
    const currency = trip.budgetCurrency === 'USD' ? '$' : trip.budgetCurrency === 'EUR' ? '€' : trip.budgetCurrency === 'GBP' ? '£' : '₹';
    addText(`Budget: ${currency}${trip.budget.toLocaleString()} per person`, 11);
  }
  
  yPosition += 10;

  // Daily Itinerary
  if (trip.itinerary?.day_by_day_plan && trip.itinerary.day_by_day_plan.length > 0) {
    addText('Daily Itinerary', 16, true, [147, 51, 234]);
    
    trip.itinerary.day_by_day_plan.forEach((day: any) => {
      if (yPosition > 250) {
        doc.addPage();
        yPosition = 20;
      }
      
      addText(`Day ${day.day}${day.date ? ` - ${new Date(day.date).toLocaleDateString()}` : ''}`, 14, true);
      addText(`Morning: ${day.morning}`, 10);
      addText(`Afternoon: ${day.afternoon}`, 10);
      addText(`Evening: ${day.evening}`, 10);
      if (day.notes) {
        addText(`Notes: ${day.notes}`, 10, false, [100, 100, 100]);
      }
      yPosition += 5;
    });
  }

  // Hotels
  if (trip.itinerary?.hotels && trip.itinerary.hotels.length > 0) {
    doc.addPage();
    yPosition = 20;
    addText('Recommended Hotels', 16, true, [147, 51, 234]);
    
    trip.itinerary.hotels.forEach((hotel: any) => {
      if (yPosition > 250) {
        doc.addPage();
        yPosition = 20;
      }
      
      addText(hotel.hotel_name, 12, true);
      addText(`Price: ${hotel.price}`, 10);
      if (hotel.rating) {
        addText(`Rating: ${hotel.rating} ⭐`, 10);
      }
      if (hotel.address) {
        addText(`Address: ${hotel.address}`, 10);
      }
      if (hotel.amenities && hotel.amenities.length > 0) {
        addText(`Amenities: ${hotel.amenities.join(', ')}`, 10);
      }
      yPosition += 5;
    });
  }

  // Flights
  if (trip.itinerary?.flights && trip.itinerary.flights.length > 0) {
    doc.addPage();
    yPosition = 20;
    addText('Flight Options', 16, true, [147, 51, 234]);
    
    trip.itinerary.flights
      .filter((flight: any) => flight.airline !== 'TBD' && flight.departure_time !== 'TBD')
      .forEach((flight: any) => {
        if (yPosition > 250) {
          doc.addPage();
          yPosition = 20;
        }
        
        addText(`${flight.airline}${flight.flight_number ? ` - ${flight.flight_number}` : ''}`, 12, true);
        addText(`Price: ${flight.price}`, 10);
        addText(`Duration: ${flight.duration}`, 10);
        addText(`Departure: ${flight.departure_time} | Arrival: ${flight.arrival_time}`, 10);
        if (typeof flight.stops !== 'undefined') {
          addText(`Stops: ${flight.stops}`, 10);
        }
        yPosition += 5;
      });
  }

  // Restaurants
  if (trip.itinerary?.restaurants && trip.itinerary.restaurants.length > 0) {
    doc.addPage();
    yPosition = 20;
    addText('Dining Recommendations', 16, true, [147, 51, 234]);
    
    trip.itinerary.restaurants.forEach((restaurant: any) => {
      if (yPosition > 250) {
        doc.addPage();
        yPosition = 20;
      }
      
      addText(restaurant.name, 12, true);
      if (restaurant.location) {
        addText(`Location: ${restaurant.location}`, 10);
      }
      if (restaurant.description) {
        addText(restaurant.description, 10);
      }
      yPosition += 5;
    });
  }

  // Budget Information
  if (trip.budget_agent_response) {
    doc.addPage();
    yPosition = 20;
    addText('Budget Analysis', 16, true, [147, 51, 234]);
    
    // Clean markdown formatting
    const cleanBudget = trip.budget_agent_response
      .replace(/#{1,6}\s/g, '')
      .replace(/\*\*/g, '')
      .replace(/\*/g, '')
      .substring(0, 2000); // Limit text length
    
    addText(cleanBudget, 10);
  }

  // Product Recommendations
  const products = trip.product_recommendations || trip.products || [];
  if (products.length > 0) {
    doc.addPage();
    yPosition = 20;
    addText('Recommended Products', 16, true, [147, 51, 234]);
    
    products.forEach((product: any) => {
      if (yPosition > 250) {
        doc.addPage();
        yPosition = 20;
      }
      
      addText(product.name, 12, true);
      const reason = product.why_needed || product.reason || 'Useful for your trip';
      addText(reason, 10);
      yPosition += 3;
    });
  }

  // Destination Highlights
  if (trip.images && trip.images.length > 0) {
    doc.addPage();
    yPosition = 20;
    addText('Destination Highlights', 16, true, [147, 51, 234]);
    
    trip.images.forEach((img: any) => {
      if (yPosition > 270) {
        doc.addPage();
        yPosition = 20;
      }
      addText(`📍 ${img.place}`, 11, true);
      yPosition += 3;
    });
  }

  // Footer on all pages
  const pageCount = doc.getNumberOfPages();
  for (let i = 1; i <= pageCount; i++) {
    doc.setPage(i);
    doc.setFontSize(8);
    doc.setTextColor(150, 150, 150);
    doc.text(
      `Generated by Travelethic  | Page ${i} of ${pageCount}`,
      pageWidth / 2,
      doc.internal.pageSize.getHeight() - 10,
      { align: 'center' }
    );
  }

  // Save the PDF
  const fileName = `TripCraft_${trip.destination?.replace(/\s+/g, '_')}_${new Date().toISOString().split('T')[0]}.pdf`;
  doc.save(fileName);
}
