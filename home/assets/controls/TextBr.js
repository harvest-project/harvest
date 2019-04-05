import React from 'react';

export function TextBr(props) {
    if (!props.text) {
        return null;
    }
    const lines = props.text.split('\n');
    return lines.map((line, i) => <span key={i}>
        {line}
        {i < lines.length - 1 ? <br/> : null}
    </span>);
}
