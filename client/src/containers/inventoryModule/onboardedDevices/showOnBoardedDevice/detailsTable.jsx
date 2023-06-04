import React from "react";

export default function DetailsTable(props) {
  const { detailsData } = props;
  const res = Object.entries(detailsData);
  return (
    <div>
      <div className="main_container">
        {res.map((key, ind) => (
          <div className="device_content">
            <p style={{ padding: "2px 7px" }}>
              <span
                style={{
                  float: "left",
                  width: "170px",
                  textAlign: " left",
                  paddingRight: " 10px",
                  fontSize: " 14px",
                  fontWeight: "400",
                }}
              >
                {key[0]}{" "}
              </span>
              <span style={{ padding: "0 20px" }}>:</span>
              <span
                style={{
                  paddingLeft: "30px",
                  fontSize: " 14px",
                  fontWeight: "400",
                }}
              >
                {key[1]}
              </span>
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}
