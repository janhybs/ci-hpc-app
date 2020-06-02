import React from "react";

import { ISimpleTimers } from "../models/DataModel";
import { getOptions, registerOptions } from "./BenchmarkView.Options";
import { BenchmarkViewModel, getConfigurationName, getColor } from "./BenchmarkView.Model";
import Highcharts from 'highcharts/highstock';
import HighchartsReact from "highcharts-react-official";
import Color from "color"
import { Row } from "react-bootstrap";

interface BenchmarkViewChartProps {
    model: BenchmarkViewModel;
    showBroken: boolean;
    commitFilter: string[];
    isSmall: boolean;
    hideTitle: boolean;
    detailCommit?: string;
    selectedBranch: string;

    onHover: (timer: ISimpleTimers) => void,
    onClick: (timer: ISimpleTimers) => void
}

export const BenchmarkViewChart = (props: BenchmarkViewChartProps) => {
    console.log("!!! render chart");
    
    const { model, showBroken, commitFilter, hideTitle, selectedBranch, isSmall, detailCommit, onHover, onClick } = props;
    const configurationName = getConfigurationName(model.configuration);

    const title = hideTitle ? ""
        : `${configurationName}<br /><small>(${(model.ratio * 100).toFixed(2)} % working)</small>`;

    const data = model.items
        .filter(i => !i.isBroken || showBroken)
        .filter(i => commitFilter.length == 0 ? true : commitFilter.indexOf(i.commit) >= 0)
        .filter(i => {
            
            return selectedBranch === "" ? true : (i.info?.branches ?? []).indexOf(selectedBranch) != -1
        });

    const commitInfo = new Map(data.map(c => [c.commit, c.info]));
    let options = getOptions(commitInfo);
    options.title.text = title;
    options.plotOptions.series!.animation = isSmall ? false : { duration: 200 };
    options.legend.enabled = !isSmall;
    options.chart.height = isSmall ? "256" : "700";
    /*options.tooltip.formatter = function(a) {
        try {
            onHover(this.point as unknown as ISimpleTimers);
        }catch(e) {
        }
        return "";
    }*/
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
                stickyTracking: false,
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

    return <HighchartsReact highcharts={Highcharts} options={options} />
}

interface DDProps {
    value: any,
    title: string,
    small?: boolean;
}
export const DD = (props: DDProps) => {
    const { value, title, small } = props;
    return <>
        <Row style={{ justifyContent: "space-between"}} className="mx-1">
            <strong>{title}: </strong>
            <code className={small === true ? "small" : ""}>{value}</code>
        </Row>
    </>
}