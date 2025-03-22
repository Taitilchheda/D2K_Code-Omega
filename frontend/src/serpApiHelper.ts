import axios from "axios";

const SERPAPI_KEY = "YOUR_SERPAPI_API_KEY"; // Replace with your actual SerpApi key

export const fetchImage = async (query: string) => {
  try {
    const response = await axios.get("https://serpapi.com/search", {
      params: {
        q: query,
        tbm: "isch",
        api_key: SERPAPI_KEY,
      },
    });

    // Extract the first image result
    return response.data.images_results[0]?.original || "";
  } catch (error) {
    console.error("Error fetching image from SerpApi:", error);
    return ""; // Return empty string if there's an error
  }
};
