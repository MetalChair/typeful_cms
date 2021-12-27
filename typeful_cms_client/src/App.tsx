import Modal from './components/Modal'
import './index.css'
import {HashRouter, Route, Routes} from "react-router-dom"
import Layout from './Layout'

function App() {

  return (
    <HashRouter>    
        <Routes>
          <Route path = "Create" element = {<Modal/>}></Route>
        </Routes>  
      <Layout>
        <div>

        </div>
      </Layout>
    </HashRouter>
  )
}

export default App
