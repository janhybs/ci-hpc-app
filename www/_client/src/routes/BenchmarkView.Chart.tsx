import React from "react";

import { ISimpleTimers, ISimpleTimersEx } from "../models/DataModel";
import { getOptions, registerOptions } from "./BenchmarkView.Options";
import { BenchmarkViewModel, getConfigurationName, getColor } from "./BenchmarkView.Model";
import Highcharts from 'highcharts/highstock';
import HighchartsReact from "highcharts-react-official";
import Color from "color"
import { Row } from "react-bootstrap";

interface BenchmarkViewChartProps {
    // model?: BenchmarkViewModel;
    showBroken: boolean;
    commitFilter: string[];
    isSmall: boolean;
    hideTitle: boolean;
    detailCommit?: string;
    selectedBranch: string;

    data: ISimpleTimersEx[];
    editOptions: (options: Required<Highcharts.Options>) => Required<Highcharts.Options>;

    onHover: (timer: ISimpleTimers) => void,
    onClick: (timer: ISimpleTimers) => void
}

export const BenchmarkViewChart = (props: BenchmarkViewChartProps) => {
    const { showBroken, commitFilter, hideTitle, isSmall, detailCommit, data: items, onHover, onClick, editOptions } = props;

    const data = items
        .filter(i => !i.isBroken || showBroken)
        .filter(i => commitFilter.length == 0 ? true : commitFilter.indexOf(i.commit) >= 0)

    const commitInfo = new Map(data.map(c => [c.commit, c.info]));
    let options = getOptions(commitInfo);
    options.plotOptions.series!.animation = isSmall ? false : { duration: 200 };
    options.legend.enabled = !isSmall;
    options.chart.height = isSmall ? "256" : "700";
    
    if (isSmall) {
        options.series = [
            {
                type: "line",
                name: "Median",
                stickyTracking: false,
                color: (Highcharts as any).getOptions().colors[0],
                data: data.map(i => {
                    return {
                        ...i,
                        color: getColor(i, detailCommit),
                        y: i.median
                    } as any;
                }),
                marker: {
                    enabled: isSmall,
                    radius: 2,
                },
                lineWidth: 1,
            },
        ];
    } else {
        options.series = [
            {
                allowPointSelect: true,
                type: "boxplot",
                name: "Boxplot",
                stickyTracking: true,
                color: (Highcharts as any).getOptions().colors[0],
                data: data.map(i => {
                    return {
                        ...i,
                        color: getColor(i, detailCommit)
                    } as any;
                })
            },
        ];
    }


    options = registerOptions(options, (t) => onHover(t), (t) => onClick(t));
    editOptions(options);

    return <HighchartsReact highcharts={Highcharts} options={options} />
}

interface DDProps {
    value: any,
    title: string,
    small?: boolean;
    tiny?: boolean;
}
export const DD = (props: DDProps) => {
    const { value, title, small, tiny } = props;
    const cls = tiny === true
        ? "tiny"
        : small === true 
            ? "small"
            : "";
    return <>
        <Row style={{ justifyContent: "space-between"}} className="mx-1">
            <strong>{title}: </strong>
            <code className={cls}>{value}</code>
        </Row>
    </>
}