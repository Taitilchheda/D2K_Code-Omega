import React, { useState, useEffect, useRef } from 'react';
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

const Graph: React.FC = () => {
  const [data, setData] = useState<EventData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedAnalysis, setSelectedAnalysis] = useState<number | null>(null);
  const [monthInput, setMonthInput] = useState('');
  const [showGraph, setShowGraph] = useState(false);
  const [chartData, setChartData] = useState<ChartData | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const seasonColors = {
    'Summer': '#FF6384',
    'Monsoon': '#36A2EB',
    'Autumn/Festival': '#FFCE56',
    'Winter': '#4BC0C0'
  };

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    setLoading(true);
    const file = event.target.files?.[0];
    
    if (!file) {
      setLoading(false);
      setError('No file selected');
      return;
    }

    // Check if file is a CSV
    if (file.type !== 'text/csv' && !file.name.endsWith('.csv')) {
      setLoading(false);
      setError('Please select a CSV file');
      return;
    }

    const reader = new FileReader();
    
    reader.onload = (e) => {
      const csvText = e.target?.result as string;
      
      Papa.parse(csvText, {
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
    };
    
    reader.onerror = () => {
      setLoading(false);
      setError('Failed to read the file');
    };
    
    reader.readAsText(file);
  };

  const handleAnalysisSelection = (choice: number) => {
    setSelectedAnalysis(choice);
    setShowGraph(true);
    setChartData(null); // Reset chart data
    
    // Only reset month input if not selecting option 3
    if (choice !== 3) {
      setMonthInput('');
    }
    
    generateChartData(choice);
  };

  const generateChartData = (analysisType: number) => {
    if (!data || data.length === 0) return;

    if (analysisType === 1) {
      // Event Count by Season
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
            backgroundColor: labels.map(season => seasonColors[season as keyof typeof seasonColors]),
            borderColor: labels.map(season => seasonColors[season as keyof typeof seasonColors]),
            borderWidth: 1,
          },
        ],
      });
    } else if (analysisType === 2) {
      // Event Count by Event Type
      const eventTypeCounts = data.reduce((acc, event) => {
        acc[event['Event Type']] = (acc[event['Event Type']] || 0) + 1;
        return acc;
      }, {} as { [key: string]: number });

      const sortedEventTypes = Object.keys(eventTypeCounts).sort((a, b) => eventTypeCounts[b] - eventTypeCounts[a]);
      const counts = sortedEventTypes.map((type) => eventTypeCounts[type]);

      const backgroundColors = generateColorPalette(sortedEventTypes.length);

      setChartData({
        labels: sortedEventTypes,
        datasets: [
          {
            label: 'Event Count by Event Type',
            data: counts,
            backgroundColor: backgroundColors,
            borderColor: backgroundColors.map(color => color.replace('0.7', '1')),
            borderWidth: 1,
          },
        ],
      });
    } else if (analysisType === 3 && monthInput) {
      // Frequency of Event Types in a Specific Month
      generateMonthChartData();
    }
  };

  const generateMonthChartData = () => {
    if (!monthInput) return;
    
    const monthNumber = parseInt(monthInput, 10);
    if (isNaN(monthNumber) || monthNumber < 1 || monthNumber > 12) return;

    const monthName = new Date(0, monthNumber - 1).toLocaleString('default', { month: 'long' });
    const monthEvents = data.filter((event) => event.Month === monthNumber);
    const eventTypeInMonthCounts = monthEvents.reduce((acc, event) => {
      acc[event['Event Type']] = (acc[event['Event Type']] || 0) + 1;
      return acc;
    }, {} as { [key: string]: number });

    const sortedEventTypesInMonth = Object.keys(eventTypeInMonthCounts).sort((a, b) => eventTypeInMonthCounts[b] - eventTypeInMonthCounts[a]);
    const countsInMonth = sortedEventTypesInMonth.map((type) => eventTypeInMonthCounts[type]);

    if (sortedEventTypesInMonth.length > 0) {
      const backgroundColors = generateColorPalette(sortedEventTypesInMonth.length);
      
      setChartData({
        labels: sortedEventTypesInMonth,
        datasets: [
          {
            label: `Frequency of Event Types in ${monthName}`,
            data: countsInMonth,
            backgroundColor: backgroundColors,
            borderColor: backgroundColors.map(color => color.replace('0.7', '1')),
            borderWidth: 1,
          },
        ],
      });
    }
  };

  const handleMonthInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setMonthInput(event.target.value);
    if (selectedAnalysis === 3 && event.target.value) {
      generateMonthChartData();
    }
  };

  const generateColorPalette = (count: number) => {
    const baseColors = [
      'rgba(255, 99, 132, 0.7)',
      'rgba(54, 162, 235, 0.7)',
      'rgba(255, 206, 86, 0.7)',
      'rgba(75, 192, 192, 0.7)',
      'rgba(153, 102, 255, 0.7)',
      'rgba(255, 159, 64, 0.7)',
      'rgba(199, 199, 199, 0.7)',
      'rgba(83, 102, 255, 0.7)',
      'rgba(40, 159, 100, 0.7)',
      'rgba(210, 99, 132, 0.7)',
    ];

    // If we need more colors than we have in our base palette, we'll generate them
    if (count <= baseColors.length) {
      return baseColors.slice(0, count);
    } else {
      const colors = [...baseColors];
      for (let i = baseColors.length; i < count; i++) {
        const r = Math.floor(Math.random() * 256);
        const g = Math.floor(Math.random() * 256);
        const b = Math.floor(Math.random() * 256);
        colors.push(`rgba(${r}, ${g}, ${b}, 0.7)`);
      }
      return colors;
    }
  };

  if (loading && data.length === 0) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-50">
        <div className="text-center p-8 max-w-md bg-white rounded-lg shadow-lg">
          <h2 className="text-2xl font-semibold mb-6 text-gray-800">Mumbai Event Discovery Platform</h2>
          <p className="mb-4 text-gray-700">Please select your CSV file to begin:</p>
          
          <label htmlFor="csvFileInput" className="block w-full px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition cursor-pointer text-center">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 inline-block mr-2" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zM6.293 6.707a1 1 0 010-1.414l3-3a1 1 0 011.414 0l3 3a1 1 0 01-1.414 1.414L11 5.414V13a1 1 0 11-2 0V5.414L7.707 6.707a1 1 0 01-1.414 0z" clipRule="evenodd" />
            </svg>
            Select CSV File
          </label>
          <input 
            type="file" 
            id="csvFileInput" 
            accept=".csv" 
            ref={fileInputRef}
            onChange={handleFileUpload} 
            className="hidden" 
          />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-50">
        <div className="text-center p-8 max-w-md bg-white rounded-lg shadow-lg border-l-4 border-red-500">
          <p className="text-xl text-red-600 mb-2">Error loading data</p>
          <p className="text-gray-700 mb-4">{error}</p>
          
          <button
            onClick={() => {
              setError(null);
              setLoading(true);
              if (fileInputRef.current) {
                fileInputRef.current.value = '';
              }
            }}
            className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-6xl mx-auto bg-white rounded-lg shadow-lg overflow-hidden">
        {/* Header with gradient and file selector */}
        <div className="bg-gradient-to-r from-blue-600 to-indigo-700 p-6 text-white">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold mb-2">Mumbai Event Discovery Platform</h1>
              <div className="flex items-center space-x-2">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M5.05 4.05a7 7 0 119.9 9.9L10 18.9l-4.95-4.95a7 7 0 010-9.9zM10 11a2 2 0 100-4 2 2 0 000 4z" clipRule="evenodd" />
                </svg>
                <p className="text-lg">Mumbai, Maharashtra, India</p>
              </div>
            </div>
            <div>
              <label htmlFor="csvFileInput" className="inline-flex items-center px-4 py-2 bg-white text-blue-700 rounded-lg hover:bg-blue-50 transition cursor-pointer">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zM6.293 6.707a1 1 0 010-1.414l3-3a1 1 0 011.414 0l3 3a1 1 0 01-1.414 1.414L11 5.414V13a1 1 0 11-2 0V5.414L7.707 6.707a1 1 0 01-1.414 0z" clipRule="evenodd" />
                </svg>
                {data.length > 0 ? 'Change CSV File' : 'Select CSV File'}
              </label>
              <input 
                type="file" 
                id="csvFileInput" 
                accept=".csv" 
                ref={fileInputRef}
                onChange={handleFileUpload} 
                className="hidden" 
              />
            </div>
          </div>
        </div>

        {/* Main content */}
        <div className="p-6">
          {loading && data.length > 0 ? (
            <div className="flex items-center justify-center h-64">
              <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
              <p className="ml-4 text-xl text-gray-700">Processing data...</p>
            </div>
          ) : (
            <>
              <h2 className="text-2xl font-semibold mb-4 text-gray-800">Trend Analysis</h2>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
                <button 
                  onClick={() => handleAnalysisSelection(1)}
                  className={`p-4 rounded-lg shadow transition-all ${selectedAnalysis === 1 ? 'bg-blue-100 border-2 border-blue-500' : 'bg-white border border-gray-200 hover:bg-gray-50'}`}
                >
                  <div className="flex flex-col items-center">
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-blue-500 mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                    </svg>
                    <span className="font-medium text-gray-800">Event Count by Season</span>
                  </div>
                </button>
                
                <button 
                  onClick={() => handleAnalysisSelection(2)}
                  className={`p-4 rounded-lg shadow transition-all ${selectedAnalysis === 2 ? 'bg-blue-100 border-2 border-blue-500' : 'bg-white border border-gray-200 hover:bg-gray-50'}`}
                >
                  <div className="flex flex-col items-center">
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-blue-500 mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z" />
                    </svg>
                    <span className="font-medium text-gray-800">Event Count by Event Type</span>
                  </div>
                </button>
                
                <div className={`p-4 rounded-lg shadow ${selectedAnalysis === 3 ? 'bg-blue-100 border-2 border-blue-500' : 'bg-white border border-gray-200'}`}>
                  <div className="flex flex-col items-center">
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-blue-500 mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                    </svg>
                    <span className="font-medium text-gray-800 mb-2">Event Types by Month</span>
                    
                    <div className="w-full mt-2">
                      <div className="flex items-center">
                        <input
                          type="number"
                          id="monthInput"
                          value={monthInput}
                          onChange={handleMonthInputChange}
                          placeholder="Enter month (1-12)"
                          min="1"
                          max="12"
                          className="flex-grow px-3 py-2 border rounded-l text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                        <button 
                          onClick={() => handleAnalysisSelection(3)}
                          className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-r focus:outline-none"
                        >
                          Go
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              
              {/* Reset button */}
              {selectedAnalysis !== null && (
                <div className="flex justify-center mb-6">
                  <button 
                    onClick={() => {
                      setSelectedAnalysis(null);
                      setShowGraph(false);
                      setChartData(null);
                      setMonthInput('');
                    }}
                    className="bg-gray-200 hover:bg-gray-300 text-gray-700 px-4 py-2 rounded-full flex items-center focus:outline-none"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                    </svg>
                    Reset Analysis
                  </button>
                </div>
              )}

              {/* Graph container */}
              <div className="bg-white p-4 rounded-lg shadow-md">
                {!showGraph || !chartData ? (
                  <div className="flex flex-col items-center justify-center h-64 text-center text-gray-500">
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-16 w-16 mb-4 text-gray-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                    </svg>
                    <p className="text-lg">Select an analysis option to view a graph</p>
                    <p className="text-sm max-w-md mt-2">Choose from the options above to visualize event data by season, type, or monthly distribution.</p>
                  </div>
                ) : (
                  <div className="h-96">
                    <Bar 
                      data={chartData} 
                      options={{
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                          legend: {
                            position: 'top',
                          },
                          title: {
                            display: true,
                            text: chartData.datasets[0].label,
                            font: {
                              size: 16,
                              weight: 'bold'
                            }
                          },
                        },
                        scales: {
                          y: {
                            beginAtZero: true,
                            grid: {
                              color: 'rgba(0, 0, 0, 0.05)',
                            },
                          },
                          x: {
                            grid: {
                              display: false,
                            },
                          },
                        },
                      }}
                    />
                  </div>
                )}
                
                {selectedAnalysis === 3 && chartData === null && monthInput && (
                  <div className="text-center p-6 text-red-500">
                    <p>No events found for the selected month. Please try another month.</p>
                  </div>
                )}
              </div>
            </>
          )}
        </div>
        
        {/* Footer */}
        <div className="bg-gray-100 p-4 border-t border-gray-200 text-center text-gray-600 text-sm">
          <p>© 2025 Mumbai Event Discovery Platform. Visualizing local events since 2022.</p>
        </div>
      </div>
    </div>
  );
};

export default Graph;