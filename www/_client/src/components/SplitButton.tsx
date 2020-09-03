import React from 'react';

import Grid from '@material-ui/core/Grid';
import Button from '@material-ui/core/Button';
import ButtonGroup from '@material-ui/core/ButtonGroup';
import ArrowDropDownIcon from '@material-ui/icons/ArrowDropDown';
import ClickAwayListener from '@material-ui/core/ClickAwayListener';
import Paper from '@material-ui/core/Paper';
import MenuItem from '@material-ui/core/MenuItem';
import MenuList from '@material-ui/core/MenuList';
import { Dialog, DialogTitle } from '@material-ui/core';


interface INameValue {
    name: string;
    value: string;
}

interface SplitButtonParams {
    title: string;
    optionsTitle: string;
    options: INameValue[];
    onChange(newValue: INameValue): void;
    onClick(): void;
    className?: string;
}

export const SplitButton = (params: SplitButtonParams) => {
    const { title, options, optionsTitle, onChange, onClick, className } = params;
    const [open, setOpen] = React.useState(false);
    const anchorRef = React.useRef(null);
    const [selectedIndex, setSelectedIndex] = React.useState(0);

    const handleClick = () => {
        onClick();
    };

    const handleMenuItemClick = (event, index) => {
        setSelectedIndex(index);
        setOpen(false);
        onChange(options[index]);
    };

    const handleToggle = () => {
        setOpen((prevOpen) => !prevOpen);
    };

    const handleClose = (event) => {
        if (anchorRef !== null && anchorRef.current !== null && (anchorRef as any).current.contains(event.target)) {
            return;
        }

        setOpen(false);
    };

    return (<>
        <Grid container direction="column" alignItems="center">
            <Grid item xs={12}>
                <ButtonGroup variant="text" color="inherit" ref={anchorRef} aria-label="split button">
                    <Button onClick={handleClick} className={className}>{title}</Button>
                    <Button
                        aria-controls={open ? 'split-button-menu' : undefined}
                        aria-expanded={open ? 'true' : undefined}
                        aria-label="select merge strategy"
                        aria-haspopup="menu"
                        onClick={handleToggle}
                    >{options[selectedIndex].name}<ArrowDropDownIcon />
                    </Button>
                </ButtonGroup>
            </Grid>
        </Grid>
        <Dialog open={open}>
            <DialogTitle>{optionsTitle}</DialogTitle>
            <Paper>
                <ClickAwayListener onClickAway={handleClose}>
                    <MenuList id="split-button-menu">
                        {options.map((option, index) => (
                            <MenuItem
                                key={option.value}
                                selected={index === selectedIndex}
                                onClick={(event) => handleMenuItemClick(event, index)}
                            >{option.name} ({option.value.substr(0, 12)})
                            </MenuItem>
                        ))}
                    </MenuList>
                </ClickAwayListener>
            </Paper>
        </Dialog>
    </>);
}