import { BarLoader } from "react-spinners";
import React from "react";
// import "../styles/spinners.css"

interface SimpleLoaderProps {
    color?: string;
    message?: string;
}

export const SimpleLoader = (props: SimpleLoaderProps) =>
    <>
        <div className="loading-wrapper">
            <div>
                <BarLoader color={props.color || "#28a745"} />
                <span>{props.message || "loading..."}</span>
            </div>
        </div>
    </>