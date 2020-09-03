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


interface INameValue<T> {
    name: string;
    value: T;
}

interface DropDownButtonParams<T> {
    optionsTitle: string;
    options: INameValue<T>[];
    onChange(newValue: INameValue<T>): void;
    className?: string;
    defaultIndex: number;
}

export const DropDownButton = <T extends object>(params: DropDownButtonParams<T>) => {
    const { optionsTitle, options, onChange, className, defaultIndex } = params;
    const [open, setOpen] = React.useState(false);
    const anchorRef = React.useRef(null);
    const [selectedIndex, setSelectedIndex] = React.useState(defaultIndex);

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
        <Button
            variant="text" color="inherit"
            aria-controls={open ? 'split-button-menu' : undefined}
            aria-expanded={open ? 'true' : undefined}
            aria-label="select merge strategy"
            aria-haspopup="menu"
            onClick={handleToggle}>
                {options[selectedIndex].name}<ArrowDropDownIcon />
        </Button>
        <Dialog open={open}>
            <DialogTitle>{optionsTitle}</DialogTitle>
            <Paper>
                <ClickAwayListener onClickAway={handleClose}>
                    <MenuList id="split-button-menu">
                        {options.map((option, index) => (
                            <MenuItem
                                key={index}
                                selected={index === selectedIndex}
                                onClick={(event) => handleMenuItemClick(event, index)}
                            >{option.name}
                            </MenuItem>
                        ))}
                    </MenuList>
                </ClickAwayListener>
            </Paper>
        </Dialog>
    </>);
}