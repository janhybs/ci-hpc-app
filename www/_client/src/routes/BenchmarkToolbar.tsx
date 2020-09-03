import React from "react";
import { Button, ButtonGroup, Box, Toolbar, AppBar } from '@material-ui/core';
import { baselines } from "../init";
import { SplitButton } from "../components/SplitButton";
import { IIndexInfo } from "../models/DataModel";
import { getConfigurationName } from "./BenchmarkView.Model";
import { DropDownButton } from "../components/DropDownButton";

interface INameValue {
    name: string;
    value: any;
}

export interface BenchmarkToolbarProps {
    onInit(setCommits: (commits: string[]) => void): void;
    onCompareCommits(a: string, b: string): void;

    configurations: IIndexInfo[];
    defaultConfiguration?: number;
    onConfigurationChange(cfg: IIndexInfo): void;
    
    branches: INameValue[];
    defaultBranch?: number;
    onBranchChange(br: INameValue): void;
}

export const BenchmarkToolbar = (props: BenchmarkToolbarProps) => {
    const { onInit, onCompareCommits } = props;
    const { configurations, defaultConfiguration, onConfigurationChange } = props;
    const { branches, defaultBranch, onBranchChange } = props;

    const [cmts, setCmts] = React.useState<string[]>([]);
    const [baseline, setBaseline] = React.useState(baselines[0].value);
    const [configuration, setConfiguration] = React.useState(configurations[defaultConfiguration || 0]);
    const [branch, setBranch] = React.useState(branches[defaultBranch || 0]);

    const cmtA = cmts.reverse()[0];
    const cmtB = cmts.reverse()[1];
    const cmtAText = cmtA || 'no selection';
    const cmtBText = cmtB || 'no selection';

    const handleConfigurationChange = (cfg: IIndexInfo) => {
        setConfiguration(cfg);
        onConfigurationChange(cfg);
    }

    const handleBranchChange = (br: INameValue) => {
        setBranch(br);
        onBranchChange(br);
    }

    onInit(commits => setCmts(commits));

    return <div style={{ marginBottom: "1em" }}>
        <AppBar position="static">
            <Toolbar variant="regular">
                <ButtonGroup className="mr-2">
                    <Button color="inherit" size="small" variant="text"
                        disabled={cmts.length < 2}
                        onClick={() => onCompareCommits(cmtA, cmtB)}>
                        <Box display="flex" flexDirection="column">
                            <span>Compare selected commits</span>
                            {/* <span className="small">{cmtAText.substr(0, 12)} | {cmtBText.substr(0, 12)}</span> */}
                        </Box>
                    </Button>
                </ButtonGroup>
                <ButtonGroup className="mr-2">
                    <SplitButton
                        onClick={() => onCompareCommits(cmtA, baseline)}
                        disabled={cmts.length < 1}
                        title="Compare with baseline"
                        optionsTitle="Choose baseline commit"
                        options={baselines}
                        onChange={cmt => setBaseline(cmt.value)}
                    />
                </ButtonGroup>
                <ButtonGroup className="mr-2">
                    <DropDownButton
                        optionsTitle="Select configuration"
                        defaultIndex={defaultConfiguration || 0}
                        onChange={item => handleConfigurationChange(item.value)}
                        options={configurations.map(i => { return { value: i, name: getConfigurationName(i)} })}
                    />
                </ButtonGroup>
                <ButtonGroup className="mr-2">
                    <DropDownButton
                        optionsTitle="Select Branch"
                        defaultIndex={defaultBranch || 0}
                        onChange={item => handleBranchChange(item)}
                        options={branches}
                    />
                </ButtonGroup>
            </Toolbar>
        </AppBar>
    </div>
}