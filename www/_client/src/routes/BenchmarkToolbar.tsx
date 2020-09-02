import React from "react";
import { Button, ButtonGroup, Select, MenuItem, FormControl, Box } from '@material-ui/core';
import { baselines } from "../init";


export interface BenchmarkToolbarProps {
    onInit(setCommits: (commits: string[]) => void): void;
    onCompareCommits(a: string, b: string): void;
}

export const BenchmarkToolbar = (props: BenchmarkToolbarProps) => {
    const { onInit, onCompareCommits } = props;
    const [cmts, setCmts] = React.useState<string[]>([]);
    const [baseline, setBaseline] = React.useState<string>(baselines[0].commit);
    const cmtA = cmts.reverse()[0] || 'x';
    const cmtB = cmts.reverse()[1] || 'x';

    const handleChange = (event) => {
        setBaseline(event.target.value);
      };

    onInit(commits => setCmts(commits));

    return <div style={{marginBottom: "1em"}}>
        <ButtonGroup>
            <Button variant="contained" color="primary" disabled={cmts.length < 2}
                onClick={() => onCompareCommits(cmtA, cmtB)}
                >Compare selected commits
            </Button>
            <Button disabled>{cmtA.substr(0, 6)}</Button>
            <Button disabled>{cmtB.substr(0, 6)}</Button>
        </ButtonGroup>

        <ButtonGroup>
            <Button variant="contained" color="secondary" disabled={cmts.length < 1}
                onClick={() => onCompareCommits(cmtA, baseline)}
                >Compare with baseline
            </Button>
            <Button disabled>{cmtA.substr(0, 6)}</Button>
            <Select color="secondary" value={baseline} onChange={handleChange} className="simple-select radiustlbl">
                {baselines.map(i => <MenuItem key={i.commit} value={i.commit}>{i.name} ({i.commit.substr(0, 6)})</MenuItem>)}
            </Select>
        </ButtonGroup>
    </div>
}