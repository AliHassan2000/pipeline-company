import React, { useState, useEffect } from "react";
import styled from "styled-components";

const RADIAN = Math.PI / 180;

const renderCustomizedLabel = (props) => {
  console.log("rendered");
  const {
    cx,
    cy,
    midAngle,
    outerRadius,
    fill,
    payload,
    percent,
    value,
    centerText,
    total,
  } = props;
  const sin = Math.sin(-RADIAN * midAngle);
  const cos = Math.cos(-RADIAN * midAngle);
  const sx = cx + (outerRadius + 0) * cos;
  const sy = cy + (outerRadius + 0) * sin;
  const mx = cx + (outerRadius + 20) * cos;
  const my = cy + (outerRadius + 30) * sin;
  const ex = mx + (cos >= 0 ? 1 : -1) * 20;
  const ey = my;
  const textAnchor = cos >= 0 ? "start" : "end";
  return (
    <>
      {value > 0 ? (
        <g>
          {/* <text x={cx} y={cy} textAnchor="middle" fill={fill}>
          {centerText.title}
        </text>
        <text x={cx} y={cy} dy={20} textAnchor="middle" fill={fill}>
          {centerText.value}
        </text> */}

          <path
            d={`M${sx},${sy}L${mx},${my}L${ex},${ey}`}
            stroke={fill}
            fill="none"
          />
          <circle cx={ex} cy={ey} r={2} fill={fill} stroke="none" />
          {/* <text
          style={{ fontWeight: "bold" }}
          x={ex + (cos >= 0 ? 1 : -1) * 12}
          y={ey}
          textAnchor={textAnchor}
          fill={fill}
        >
          {payload.name}
        </text> */}
          <text
            style={{ fontSize: "12px" }}
            x={ex + (cos >= 0 ? 1 : -1) * 12}
            y={ey}
            dy={3}
            textAnchor={textAnchor}
            fill="#999"
          >
            {value} ({((value / total) * 100).toFixed(2)}%)
          </text>
        </g>
      ) : null}
    </>
  );
};

export default React.memo(renderCustomizedLabel);

export const getTotal = (data) => {
  return data.reduce((total, domain) => total + domain.value, 0);
};
