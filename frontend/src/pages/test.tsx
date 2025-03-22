import React, { useState, useEffect } from 'react';
import Papa from 'papaparse';
import { Bar } from 'react-chartjs-2';
import 'chart.js/auto';

interface EventData {
  'Event Name': string;
  'Event Type': string;
  'Event Date': string;
  Day: string;
  Month: number;
  Season: string;
  Location: string;
  'Engagement Score': number;
}

interface ChartData {
  labels: string[];
  datasets: {
    label: string;
    data: number[];
    backgroundColor: string[];
    borderColor: string[];
    borderWidth: number;
  }[];
}

const Dashboard: React.FC = () => {
  const [data, setData] = useState<EventData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedAnalysis, setSelectedAnalysis] = useState<number | null>(null);
  const [monthInput, setMonthInput] = useState('');
  const [showGraph, setShowGraph] = useState(false);
  const [chartData, setChartData] = useState<ChartData | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch('/event_data.csv'); // Assuming the CSV is in the public folder
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const reader = response.body?.getReader();
        if (!reader) {
          throw new Error('Could not get reader for response body.');
        }
        const decoder = new TextDecoder();
        let csvString = '';
        while (true) {
          const { done, value } = await reader.read();
          if (done) {
            break;
          }
          csvString += decoder.decode(value);
        }

        Papa.parse(csvString, {
          header: true,
          dynamicTyping: true,
          complete: (results) => {
            setData(results.data as EventData[]);
            setLoading(false);
            setError(null);
          },
          error: (err) => {
            setLoading(false);
            setError(`Error parsing CSV: ${err.message}`);
          },
        });
      } catch (err: any) {
        setLoading(false);
        setError(err.message || 'Failed to fetch the CSV file.');
      }
    };

    fetchData();
  }, []);

  const handleAnalysisSelection = (choice: number) => {
    setSelectedAnalysis(choice);
    setShowGraph(true);
    setChartData(null); // Reset chart data
    setMonthInput(''); // Reset month input
  };

  const renderGraph = () => {
    if (!showGraph || !data || data.length === 0 || selectedAnalysis === null) {
      return <p>Select an analysis option to view a graph.</p>;
    }

    if (selectedAnalysis === 1) {
      const seasonCounts: { [key: string]: number } = {};
      data.forEach((event) => {
        seasonCounts[event.Season] = (seasonCounts[event.Season] || 0) + 1;
      });

      const labels = ['Summer', 'Monsoon', 'Autumn/Festival', 'Winter'];
      const counts = labels.map((season) => seasonCounts[season] || 0);

      setChartData({
        labels: labels,
        datasets: [
          {
            label: 'Event Count by Season',
            data: counts,
            backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0'],
            borderColor: ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0'],
            borderWidth: 1,
          },
        ],
      });
    } else if (selectedAnalysis === 2) {
      const eventTypeCounts = data.reduce((acc, event) => {
        acc[event['Event Type']] = (acc[event['Event Type']] || 0) + 1;
        return acc;
      }, {} as { [key: string]: number });

      const sortedEventTypes = Object.keys(eventTypeCounts).sort((a, b) => eventTypeCounts[b] - eventTypeCounts[a]);
      const counts = sortedEventTypes.map((type) => eventTypeCounts[type]);

      setChartData({
        labels: sortedEventTypes,
        datasets: [
          {
            label: 'Event Count by Event Type',
            data: counts,
            backgroundColor: sortedEventTypes.map(() => getRandomColor()),
            borderColor: sortedEventTypes.map(() => getRandomColor()),
            borderWidth: 1,
          },
        ],
      });
    } else if (selectedAnalysis === 3) {
      if (!monthInput) {
        return <p>Please enter a month number to see the graph.</p>;
      }
      const monthNumber = parseInt(monthInput, 10);
      if (isNaN(monthNumber) || monthNumber < 1 || monthNumber > 12) {
        return <p>Invalid month number. Please enter a number between 1 and 12.</p>;
      }

      const monthName = new Date(0, monthNumber - 1).toLocaleString('default', { month: 'long' });
      const monthEvents = data.filter((event) => event.Month === monthNumber);
      const eventTypeInMonthCounts = monthEvents.reduce((acc, event) => {
        acc[event['Event Type']] = (acc[event['Event Type']] || 0) + 1;
        return acc;
      }, {} as { [key: string]: number });

      const sortedEventTypesInMonth = Object.keys(eventTypeInMonthCounts).sort((a, b) => eventTypeInMonthCounts[b] - eventTypeInMonthCounts[a]);
      const countsInMonth = sortedEventTypesInMonth.map((type) => eventTypeInMonthCounts[type]);

      if (sortedEventTypesInMonth.length > 0) {
        setChartData({
          labels: sortedEventTypesInMonth,
          datasets: [
            {
              label: `Frequency of Event Types in ${monthName}`,
              data: countsInMonth,
              backgroundColor: sortedEventTypesInMonth.map(() => getRandomColor()),
              borderColor: sortedEventTypesInMonth.map(() => getRandomColor()),
              borderWidth: 1,
            },
          ],
        });
      } else {
        return <p>No events found for the month of {monthName}.</p>;
      }
    }

    if (chartData) {
      return (
        <div style={{ width: '80%', margin: '20px auto' }}>
          <Bar data={chartData} />
        </div>
      );
    }

    return null;
  };

  const handleMonthInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setMonthInput(event.target.value);
  };

  const getRandomColor = () => {
    const r = Math.floor(Math.random() * 256);
    const g = Math.floor(Math.random() * 256);
    const b = Math.floor(Math.random() * 256);
    return `rgb(${r}, ${g}, ${b})`;
  };

  if (loading) {
    return <p>Loading event data...</p>;
  }

  if (error) {
    return <p style={{ color: 'red' }}>Error loading data: {error}</p>;
  }

  return (
    <div>
      <h1>Mumbai Event Discovery Platform Dashboard</h1>
      <p>Current Location: Mumbai, Maharashtra, India</p>

      <h2>Choose Analysis:</h2>
      <ul>
        <li><button onClick={() => handleAnalysisSelection(1)}>1. Event Count by Season</button></li>
        <li><button onClick={() => handleAnalysisSelection(2)}>2. Event Count by Event Type</button></li>
        <li>
          <button onClick={() => handleAnalysisSelection(3)}>3. Frequency of Event Types in a Specific Month</button>
          {selectedAnalysis === 3 && (
            <div>
              <label htmlFor="monthInput">Enter Month Number (1-12): </label>
              <input
                type="number"
                id="monthInput"
                value={monthInput}
                onChange={handleMonthInputChange}
              />
            </div>
          )}
        </li>
        <li><button onClick={() => setSelectedAnalysis(null) || setShowGraph(false) || setChartData(null) || setMonthInput('')}>Clear Analysis</button></li>
      </ul>

      {renderGraph()}
    </div>
  );
};

export default Dashboard;