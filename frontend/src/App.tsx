import Main from "./pages/App"
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Recommendation from "./pages/Recommendation"
function App() {


  return (
    <>
     <BrowserRouter>
      <Routes>
        <Route path="/" element={<Main/>}/>
          <Route path="/recommend" element={<Recommendation />} />
        {/* </Route> */}
      </Routes>
    </BrowserRouter>
    </>
  )
}

export default App
