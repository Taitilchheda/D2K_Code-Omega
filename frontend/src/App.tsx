import Main from "./pages/App"
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Recommendation from "./pages/Recommendation"
import HomePage from "./pages/Home";
import EventDetailPage from "./pages/EventDetails";
function App() {


  return (
    <>
     <BrowserRouter>
      <Routes>
        <Route path="/" element={<Main/>}/>
          <Route path="/recommend" element={<Recommendation />} />
          <Route path="/home" element={<HomePage />} />
          <Route path="/event/:id" element={<EventDetailPage />} />
          <Route path="/movie/:id" element={<EventDetailPage />} />
          {/* </Route> */}
        {/* </Route> */}
      </Routes>
    </BrowserRouter>
    </>
  )
}

export default App