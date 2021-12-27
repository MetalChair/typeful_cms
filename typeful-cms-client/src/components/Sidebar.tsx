import {FaPen} from "react-icons/fa"
import {Route, Routes, Link} from "react-router-dom"
import Modal from "./Modal"
export default function Sidebar(){
    return(
        <div className = "w-1/6 absolute shadow-xl h-full bg-white flex flex-col">
            <div className = "bg-blue-600 h-16 text-white font-bold text-xl flex flex-row justify-center items-center">
                Typeful CMS
            </div>
            <div className = "flex flex-col w-full text-gray-900 text-left">
                <Link to = "Create">
                    <div className = "nav-item">
                            <div className = "nav-icon">
                                    <FaPen/>
                            </div>
                            <span>Create New Model</span>
                    </div>
                </Link>
            </div>
        </div>
    )
}