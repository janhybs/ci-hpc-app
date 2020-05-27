import { IGitInfo, ISimpleTimers } from "../models/DataModel";
import moment from "moment";
import { SeriesBoxplotOptions } from "highcharts";


export const registerOptions = (
    options: Required<Highcharts.Options>,
    onHover: (timer: ISimpleTimers) => void,
    onClick: (timer: ISimpleTimers) => void,
) => {

    const boxplot = options.series?.find(i => i.type == "boxplot") as SeriesBoxplotOptions;
    if (boxplot) {
        boxplot.point = !boxplot.point ? {} : boxplot.point;
        boxplot.point.events = !boxplot.point.events ? {} : boxplot.point.events;
        boxplot.point.events.mouseOver = function () {
            onHover(this as unknown as ISimpleTimers);
        }
        boxplot.point.events.click = function () {
            onClick(this as unknown as ISimpleTimers);
        }
        boxplot.point.events.mouseOut = function () { }
    }
    return options;
}

export const getOptions = (commitInfo: Map<string, IGitInfo>): Required<Highcharts.Options> => {
    const xLabels = [...commitInfo.keys()];

    return {
        title: {
            text: undefined,
        },
        credits: {
            enabled: false
        },
        plotOptions: {
            series: {
                turboThreshold: 0,
            }
        },
        legend: {
            enabled: false
        },
        yAxis: {
            title: {
                text: null,
            },
        },
        xAxis: {
            crosshair: {
                width: 1,
                snap: false
            },
            title: {
                text: null,
            },
            labels: {
                formatter: ({ value }) => {
                    const sha = xLabels[value];
                    if (!sha) {
                        return "<invalid commit>";
                    }

                    const commit = commitInfo.get(sha);
                    if (!commit) {
                        return "<invalid commit>";
                    }

                    return `${moment(commit.date as any).fromNow(true)} - ${commit.branch || [...commit.branches].splice(0, 3)}`
                },
                style: {
                    fontSize: "9px"
                }
            }
        },
        tooltip: {
            enabled: false,
            shadow: false,
            borderWidth: 0,
            backgroundColor: 'rgba(255,255,255,0.8)',
            positioner: function (a, b, c) {
                return { x: 10, y: 10 };
            },
            /*formatter: function(a, b) {
                return "";
            }*/
            // useHTML: true,
            // snap: 0,
        },
        chart: {
            zoomType: "x",
            // events: {
            //     load: function (ev) {
            //         if (defaultZoom) {
            //             const chart = this as any;
            //             chart.xAxis[0].setExtremes(
            //                 chart.series[0].xData.length - maxCommitByDefault,
            //                 chart.series[0].xData.length
            //             );
            //             chart.showResetZoom();
            //         }
            //     },
            // }
        }
    } as Required<Highcharts.Options>;
};