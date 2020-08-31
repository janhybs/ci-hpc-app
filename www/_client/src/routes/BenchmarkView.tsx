import React from "react";

import { observer } from "mobx-react"
import { observable, action } from "mobx"
import { httpClient, configurations } from "../init";
import { ITimersFilter, IIndexInfo, ISimpleTimers, ISimpleTimersEx, ICompareCommitFilter, ICompareCommitDto, IDurInfo } from "../models/DataModel";
import Dropdown from 'react-bootstrap/Dropdown'
import { DropdownButton, Button, ButtonToolbar, ButtonGroup, Alert, Row } from "react-bootstrap";
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faRedo } from '@fortawesome/free-solid-svg-icons'
import Color from "color"

import moment from "moment";
import "../styles/chart.css";

import HighchartsReact from 'highcharts-react-official';
import Highcharts from 'highcharts/highstock';
import addHighchartsMore from 'highcharts/highcharts-more';
import { NotificationApi } from "../utils/Notification";
import { SimpleLoader } from "../components/SimpleLoader";
import { getOptions, registerOptions } from "./BenchmarkView.Options";
import { BenchmarkViewModel, getConfigurationName, trimSha } from "./BenchmarkView.Model";
import { BenchmarkViewChart, DD } from "./BenchmarkView.Chart";
import { Col } from "reactstrap";
import { RenderStats } from "./BenchmarView.Stats";
import { countUnique } from "../utils/MapUtils";
addHighchartsMore(Highcharts);


(window as any).Color = Color;
(window as any).Highcharts = Highcharts;
const defaultFormat = (i: any) => i.toFixed(2);


const outlierCoef = 0.25;

interface BenchmarkViewState {
    model: BenchmarkViewModel;
    foo: number;
}


export interface BenchmarkViewProps {
    simple?: boolean;
    hideTitle?: boolean;
    hideXTicks?: boolean;
    configuration?: IIndexInfo;
    size?: "big" | "small";

    hideBroken?: boolean
}

@observer
export class BenchmarkView extends React.Component<BenchmarkViewProps, BenchmarkViewState, {}> {

    @observable
    public model = new BenchmarkViewModel()

    @observable
    private showBroken = false;

    @observable
    private showTooltip = false;

    @observable
    private commitFilter: string[] = [];

    private oldCommitSha: string = "";

    @observable
    private timerLocked: boolean = false;

    @observable
    private selectedBranch: string = "master";

    private setTimer: any;

    @observable
    private commitQueue: string[] = [];

    @observable
    private stackChart: any = null;

    constructor(state) {
        super(state);

        const match = (this.props as any).match;
        const index = match ? match.params.index : null;

        if (this.props.configuration != null) {
            this.model.configuration = this.props.configuration
        } else if (index != null) {
            this.model.configuration = configurations[index] as IIndexInfo;
        }
        this.model.configuration.branch = this.model.configuration.branch || "master";
        this.load();
        window.addEventListener("keydown", e => this.handleKeyDown(e));
    }

    load() {
        httpClient.fetch<ISimpleTimers[]>("timers/list", this.model.filter)
            .then((json: any) => {

                let rawData = json.data as ISimpleTimers[];

                if (this.props.hideBroken === true) {
                    rawData = rawData
                        .filter(i => i.isBroken === false);
                }

                const data: ISimpleTimersEx[] = rawData.map(
                    i => {
                        const dur = i.durations || [0, 0, 0];
                        const len = dur.length;
                        const int = Math.floor;

                        return {
                            ...i,
                            low: Math.min(...dur),
                            high: Math.max(...dur),
                            median: dur[int(len / 2)],
                            q1: dur[int(len * 0.25)],
                            q3: dur[int(len * 0.75)],
                        }
                    }
                )

                this.model.items = data;
                this.model.ratio = json.ratio;

                this.setState({ foo: Math.random() });
                NotificationApi.success('Data loaded', "", 1000);
            });
    }

    switchConfig(item: IIndexInfo) {
        this.model.configuration = item;
        this.load();
    }

    changeBranch(branch: string) {
        this.selectedBranch = branch;
        this.model.configuration.branch = branch;
        this.load();
    }

    @action.bound
    handleKeyDown(e: KeyboardEvent) {
        if (e.key === "Shift") {
            this.showTooltip = !this.showTooltip;
        }
    }

    compareCommitsDefault() {
        this.compareCommits(this.commitQueue[0], this.commitQueue[1], '/whole-program');
    }

    compareCommits(commitA: string, commitB: string, frame: string) {
        const filter: ICompareCommitFilter = {
            info: this.model.configuration,
            commitA: commitA,
            commitB: commitB,
            frame: frame,
        };
        const that = this;
        httpClient.fetch<ICompareCommitDto>("compare-commit/compare-ab", filter)
            .then(i => {
                const framesA = i.commitA.map(j => j.frame);
                const framesB = i.commitB.map(j => j.frame);

                // assuming framesA.length == framesB.length;
                
                const frameAData = framesA.map((j, k) => {
                    return {
                        stack: 'A',
                        name: j,
                        data: [
                            i.commitA[k].duration.avg,
                            i.commitB[k].duration.avg
                        ],
                    }
                });
                const d: Highcharts.Options = {
                    title: {
                        text: undefined,
                    },
                    chart: {
                        type: "column",
                        height: 600,
                    },
                    xAxis: {
                        categories: [
                            `${filter.commitA.substr(0,6)} [${i.rootA.duration.avg.toFixed(3)} sec]`,
                            `${filter.commitB.substr(0,6)} [${i.rootB.duration.avg.toFixed(3)} sec]`,
                        ]
                    },
                    plotOptions: {
                        series: {
                            events: {
                                click: function() {
                                    that.compareCommits(
                                        filter.commitA, filter.commitB,
                                        `${filter.frame}/${this.name}`
                                    );
                                }
                            }
                        },
                        column: {
                            stacking: 'normal',
                        }
                    },
                    series: [...frameAData as any],
                };
                this.stackChart = {options: d, filter: filter};
            });
    }

    @action.bound
    rememberCommit(commit: string) {
        if (this.commitQueue.includes(commit)) {
            return;
        }

        this.commitQueue.push(commit);
        this.commitQueue = this.commitQueue.slice(-2);
    }

    render() {
        const { commitFilter, model, showBroken, oldCommitSha, selectedBranch } = this;
        const configurationName = getConfigurationName(model.configuration);
        const { size, simple, hideTitle } = this.props;
        const isSmall = size === "small";
        const isSimple = simple === true;
        const data = model.items;
        const detailMode = commitFilter.length > 0;


        const handleClick = (timer: ISimpleTimers) => {
            this.rememberCommit(timer.commit);
            if (!this.setTimer) {
                return;
            }
            this.setTimer(timer);
            this.timerLocked = !this.timerLocked;
        }

        const handleHover = (timer: ISimpleTimers) => {
            if (!this.setTimer) {
                return;
            }
            
            if (!this.timerLocked) {
                this.setTimer(timer);
            }
        }

        if (model.items.length === 0) {
            return <SimpleLoader />
        }

        const branches = new Map([
            ["", data.length],
            ...countUnique(
                data.filter(i => i.isBroken === false)
                    .flatMap(i => i.info?.branches || [])
                    .filter(i => i != null))
                .entries()
            ]);

        return <>
            <Row>
                <Col>
                    <Button disabled={this.commitQueue.length <= 1} onClick={() => this.compareCommitsDefault()}>
                        Compare Commits {this.commitQueue.map(i => i.substr(0,6)).join(', ')}
                    </Button>
                </Col>
            </Row>
            {this.stackChart !== null && <>
                <Row>
                    <ButtonGroup>
                        {(this.stackChart.filter.frame as string)
                            .split("/")
                            .map((i, j) => <Button onClick={() => this.compareCommits(
                                this.stackChart.filter.commitA,
                                this.stackChart.filter.commitB,
                                `${this.stackChart.filter.frame.split("/").slice(0, j+1).join('/')}`
                            )}>
                                {i}
                            </Button>)}
                    </ButtonGroup>
                </Row>
                <Row>
                    <HighchartsReact
                        highcharts={Highcharts}
                        options={this.stackChart.options}/>
                </Row>
            </>}
            {!simple &&
                <Row>
                    <ButtonToolbar>
                        <ButtonGroup>
                            <Button variant="dark" onClick={(i) => this.load()}>
                                <FontAwesomeIcon icon={faRedo} />
                            </Button>
                            <DropdownButton id="dropdown-basic-button"
                                title={`${configurationName} [${data.length} commits]`} as={ButtonGroup}>
                                {configurations.map((item, j) =>
                                    <Dropdown.Item
                                        key={getConfigurationName(item)}
                                        onSelect={i => {
                                            this.switchConfig(item);
                                            (this.props as any).history.push(`/benchmarks/${j}`);
                                        }}
                                        active={configurationName === getConfigurationName(item)}
                                    >
                                        {getConfigurationName(item)}
                                    </Dropdown.Item>
                                )}
                            </DropdownButton>
                        </ButtonGroup>
                        <Button onClick={() => this.showBroken = !showBroken}>
                            Toggle broken builds
                        </Button>
                        <DropdownButton
                            id="dropdown-branch"
                            title={selectedBranch ? selectedBranch : "<Select branch>"}
                            value={selectedBranch}
                            >
                            {[...branches.entries()]
                                .slice(0, 55)
                                .map(i => {
                                    return <Dropdown.Item key={i[0]}
                                        onSelect={() => this.changeBranch(i[0])}>
                                        {i[0]} ({i[1]} cmts)
                                    </Dropdown.Item>
                            })}
                            
                        </DropdownButton>
                    </ButtonToolbar>
                </Row>
            }
            <Row>
                <Col lg={isSmall ? 12 : 9}>
                    <BenchmarkViewChart
                        commitFilter={commitFilter}
                        hideTitle={hideTitle === true}
                        isSmall={isSmall}
                        model={model}
                        showBroken={showBroken}
                        detailCommit={oldCommitSha}
                        selectedBranch={selectedBranch}
                        onClick={timer => handleClick(timer)}
                        onHover={timer => handleHover(timer)}
                    />
                </Col>
                {!isSmall &&
                    <Col lg={3}>
                        <RenderStats
                            onInit={setTimer => this.setTimer = setTimer}
                            timers={data}
                        />
                    </Col>}
            </Row>
        </>
    }
}