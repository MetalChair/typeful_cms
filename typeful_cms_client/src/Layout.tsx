import Sidebar from "./components/Sidebar";

interface LayoutProps{
    children : JSX.Element
}

export default function Layout ({children} : LayoutProps){
    return(
        <div className = "w-full h-full">
            <Sidebar/>
            <div className = "w-full h-full bg-gray-200">
                {children}
            </div>
        </div>
    )
}