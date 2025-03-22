import Main from "./pages/App"
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Recommendation from "./pages/Recommendation"
import HomePage from "./pages/Home";
import EventDetailPage from "./pages/EventDetails";
import Graph from "./pages/test";
import Dashboard from "./pages/Dashboad";
import { UserLogin } from "./pages/Login";

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
          <Route path="/test" element={<Graph/>} />
          <Route path="/Dashboard" element={<Dashboard/>} />
          <Route path="/login" element={<UserLogin/>} />
          {/* </Route> */}
        {/* </Route> */}
      </Routes>
    </BrowserRouter>
    </>
  )
}

export default App