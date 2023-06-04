import React, { useState, useEffect, PureComponent } from "react";

export class CustomizedLabel extends PureComponent {
  render() {
    const { x, y, stroke, value } = this.props;

    return (
      <text
        x={x}
        y={y}
        dx={6}
        dy={-4}
        fill={stroke}
        fontSize={10}
        textAnchor="middle"
      >
        {value === 0 ? null : value}
      </text>
    );
  }
}
