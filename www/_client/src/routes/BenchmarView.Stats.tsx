import React from "react";
import { ISimpleTimersEx } from "../models/DataModel";
import { DD } from "./BenchmarkView.Chart";
import { trimSha } from "./BenchmarkView.Model";
import { Card } from "react-bootstrap";
import Highcharts, { SeriesOptions, SeriesScatterOptions } from 'highcharts/highstock';
import HighchartsReact from "highcharts-react-official";
import bellcurve from 'highcharts/modules/histogram-bellcurve';
import Moment from "react-moment";
(bellcurve)(Highcharts);

interface RenderStatsProps {
    onInit(setTimer: (timer: ISimpleTimersEx) => void): void;

    timers: ISimpleTimersEx[];
}

const prevFill = {};
const prevStroke = {};

export const RenderStats = (props: RenderStatsProps) => {
    const { onInit, timers } = props;
    const [timer, setTimer] = React.useState<ISimpleTimersEx>({} as ISimpleTimersEx);
    onInit((newTimer) => {
        const els = ["stem", "whiskers", "box", "graphic", "medianShape"];

        els.forEach(i => {
            if (timer[i]) {
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

    if (timer == null) {
        return <> </>
    }

    const leftCommits = timer.left || [];
    const rightCommits = timer.right || [];
    const categories = [...leftCommits, ...rightCommits];
    const categoriesShort = categories.map(i => i.substr(0,6));

    const leftData = timers
        .filter(i => leftCommits.indexOf(i.commit) !== -1)
        .flatMap(i => (i.durations || [])
            .map(j => [categories.indexOf(i.commit), j]));

    const rightData = timers
        .filter(i => rightCommits.indexOf(i.commit) !== -1)
        .flatMap(i => (i.durations || [])
            .map(j => [categories.indexOf(i.commit), j]));

    const baseOpts: SeriesScatterOptions = {
        type: "scatter",
        jitter: {
            x: 0.125
        },
        marker: {
            symbol: "diamond",
            radius: 3,
        }
    };

    return <>
        <Card>
            <Card.Header>
                {"Data"}
            </Card.Header>
            <Card.Body>
                <HighchartsReact highcharts={Highcharts} options={{
                    title: {
                        text: undefined,
                    },
                    credits: {
                        enabled: false,
                    },
                    chart: {
                        height: 240,
                        plotBorderWidth: 0,
                    },
                    xAxis: {
                        categories: categoriesShort
                    },
                    series: [
                        /*{
                            type: "histogram",
                            name: "histogram",
                            baseSeries: "left",
                            zIndex: -1,
                            binsNumber: 9,
                            animation: {
                                duration: 100,
                            },
                        },
                        {
                            type: "histogram",
                            name: "histogram",
                            baseSeries: "right",
                            zIndex: -1,
                            binsNumber: 9,
                            animation: {
                                duration: 100,
                            },
                        },*/
                        {
                            ...baseOpts,
                            name: `left: (e = ${timer?.welch?.estimatedValue2.toFixed(2)})`,
                            data: leftData,
                            color: "#aa46be",
                        },
                        {
                            ...baseOpts,
                            name: `right: (e = ${timer?.welch?.estimatedValue1.toFixed(2)})`,
                            data: rightData,
                            color: "#28b4c8",
                        },
                    ]
                }} />
            </Card.Body>
        </Card>

        <Card>
            <Card.Header>
                {"Repo info"}
            </Card.Header>
            <Card.Body>
                <DD value={timer.commit} title="Commit" tiny />
                <DD title="Date" small value={<>
                    <Moment format="YYYY-MM-DD HH:mm" date={timer.info?.date} /> (<Moment fromNow date={timer.info?.date} />)
                    </>} />
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
                <DD value={timer.welch?.criticalValue.toFixed(4)} title="crit" />
                <DD value={timer.welch?.degreesOfFreedom} title="DoF" />
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