import React from "react";
import { ISimpleTimers } from "../models/DataModel";
import { DD } from "./BenchmarkView.Chart";
import { trimSha } from "./BenchmarkView.Model";
import { Card } from "react-bootstrap";


interface RenderStatsProps {
    onInit(setTimer: (timer: ISimpleTimers) => void): void;
}

const prevFill = {};
const prevStroke = {};

export const RenderStats = (props: RenderStatsProps) => {
    const { onInit } = props;
    const [timer, setTimer] = React.useState<ISimpleTimers>({} as ISimpleTimers);
    onInit((newTimer) => {
        const els = ["stem", "whiskers", "box", "graphic", "medianShape"];
        
        els.forEach(i => {
            if(timer[i]) {
                timer[i]?.element.setAttribute("fill", prevFill[i]);
                timer[i]?.element.setAttribute("stroke", prevStroke[i]);
            }
        });
        
        const t = (newTimer as any);
        els.forEach(i => {
            prevFill[i] = t[i].element.getAttribute("fill");
            prevStroke[i] = t[i].element.getAttribute("stroke");
            t[i]?.element.setAttribute("fill", "gold");
            t[i]?.element.setAttribute("stroke", "gold");
        });
        setTimer(newTimer);
    });

    return <>
        <Card>
            <Card.Header>
                {"Repo info"}
            </Card.Header>
            <Card.Body>
                <DD value={timer.commit} title="Commit" small />
                <DD value={timer.info?.message?.substr(0, 32)} title="Message" small />
                <DD value={timer.info?.branch} title="Branch" />
                <DD value={timer.info?.branches?.slice().splice(0, 4).join(", ")} title="Branches" small />
            </Card.Body>
        </Card>

        <Card>
            <Card.Header>
                {"Welch test"}
            </Card.Header>
            <Card.Body>
                <DD value={timer.welch?.n1} title="N" />
                <DD value={timer.welch?.pValue.toFixed(4)} title="pValue" />
                <DD value={timer.welch?.estimatedValue1.toFixed(4)} title="x1" />
                <DD value={timer.welch?.estimatedValue2.toFixed(4)} title="x2" />
                <DD value={timer.welch?.radius} title="radius" />
                <DD value={timer.left?.reduce(trimSha)} title="Left" />
                <DD value={timer.right?.reduce(trimSha)} title="Right" />
            </Card.Body>
        </Card>

        <Card>
            <Card.Header>
                {"Commit details"}
            </Card.Header>
            <Card.Body>
                <DD value={timer.count} title="N" />
                <DD value={timer.low?.toFixed(4)} title="Low" />
                <DD value={timer.q1?.toFixed(4)} title="Q1" />
                <DD value={timer.median?.toFixed(4)} title="Median" />
                <DD value={timer.q3?.toFixed(4)} title="Q3" />
                <DD value={timer.high?.toFixed(4)} title="High" />
            </Card.Body>
        </Card>
    </>
}