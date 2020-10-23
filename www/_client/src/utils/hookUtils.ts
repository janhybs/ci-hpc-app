import React, { useState } from "react";

export function useBool(initialValue: boolean = false): [boolean, () => void, () => void] {
    const [val, setVal] = useState(initialValue);
    
    return [val, () => setVal(true), () => setVal(false)];
}