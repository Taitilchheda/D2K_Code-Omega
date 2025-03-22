import json
import os
import requests
from dotenv import load_dotenv
from serpapi import GoogleSearch

load_dotenv()
serper_api_key = os.getenv('SERPER_API_KEY')
google_serp_api_key = os.getenv('GOOGLE_SERP_API_KEY')

class SerperProvider:
    @staticmethod
    def module_image_from_web(submodules:dict):
        print('FETCHING IMAGES...')
        keys_list = list(submodules.keys())
        url = "https://google.serper.dev/images"
        headers = {
            'X-API-KEY': serper_api_key,
            'Content-Type': 'application/json'
        }
        images_list=[]
        for key in keys_list:
            payload = json.dumps({
                "q": submodules[key]
            })
            response = requests.request("POST", url, headers=headers, data=payload)
            json_response = json.loads(response.text)
            image_results = json_response["images"]
            image_links = [i["imageUrl"] for i in image_results]
            images_list.append(image_links)
        return images_list
    
    @staticmethod
    async def submodule_image_from_web(submodule_name):
        url = "https://google.serper.dev/images"
        headers = {
            'X-API-KEY': serper_api_key,
            'Content-Type': 'application/json'
        }
        payload = json.dumps({
            "q": submodule_name
        })
        response = requests.request("POST", url, headers=headers, data=payload)
        json_response = json.loads(response.text)
        image_results = json_response["images"]
        image_links = [i["imageUrl"] for i in image_results]
        return image_links
    
    @staticmethod
    def module_videos_from_web(submodules):
        print('FETCHING VIDEOS...')
        keys_list = list(submodules.keys())
        videos_list=[]
        for key in keys_list:
            params = {
                "q": submodules[key],
                "engine": "google_videos",
                "ijn": "0",
                "api_key": google_serp_api_key
            }

            search = GoogleSearch(params)
            results = search.get_dict()
            video_results = results["video_results"]
            yt_links = [i['link'] for i in video_results[:10]]
            videos_list.append(yt_links)
        return videos_list
    
    @staticmethod
    def search_videos_from_web(query : str, n_videos : int = 5):
        params = {
            "q": query,
            "engine": "google_videos",
            "ijn": "0",
            "api_key": google_serp_api_key
        }

        search = GoogleSearch(params)
        results = search.get_dict()
        video_results = results["video_results"]
        yt_links = [i['link'] for i in video_results[:n_videos]]
        return yt_links

    @staticmethod
    def find_courses(skills : list):
        
        def extract_course_links(search_results : dict):
            """Extracts valid course links from inline sitelinks."""
            trusted_sources = ["Coursera","edX", "Udacity", "upGrad", "FutureLearn", "Udemy", "Harvard University"]
            course_links = []

            if "organic_results" not in search_results:
                return course_links
            for result in search_results.get("organic_results", []):
                source = result.get("source")
                sitelinks = result.get("sitelinks", {}).get("inline", [])
                if source in trusted_sources and sitelinks:
                    for sitelink in sitelinks:
                        link = sitelink.get("link")
                        if link :
                            course_links.append({
                                "source": source,
                                "title": sitelink.get("title", "No Title"),
                                "link": link
                            })

            return course_links
        
        course_links = []
        for skill in skills:
            params = {
                "q": f"Courses on {skill}",
                "engine": "google",
                "api_key": google_serp_api_key,
                "location": "India"
            }
            try:
                search = GoogleSearch(params)
                results = search.get_dict()
                extracted_links = extract_course_links(results)
                if extracted_links:
                    course_links = extracted_links
            except Exception as e:
                print(f"Error searching for {skill}: {e}")
        return course_links