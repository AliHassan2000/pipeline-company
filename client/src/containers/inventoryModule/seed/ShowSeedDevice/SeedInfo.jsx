import React from "react";
import "antd/dist/antd.css";
import "./index.css";
import { Table } from "antd";
export default function SeedInfo(props) {
  const { seedRecord } = props;
  const res = Object.entries(seedRecord);
  const fixedData = [];
  res !== undefined &&
    res.map((item, i) =>
      fixedData.push({
        key: i,
        name: item[0],
        description: item[1],
      })
    );
  const fixedColumns = [
    {
      title: "Name",
      dataIndex: "name",
      fixed: true,
      width: 170,
    },
    {
      title: "Description",
      dataIndex: "description",
    },
  ];

  return (
    <Table
      // pagination={{
      //   defaultPageSize: 50,
      //   pageSizeOptions: [50, 100, 500, 1000],
      // }}
      // size="small"
      // scroll={{ x: 1000, y: height - 350 }}
      style={{ fontSize: "16px !important" }}
      rowClassName={(record, index) =>
        index % 2 === 0 ? "table-row-light" : "table-row-dark"
      }
      columns={fixedColumns}
      dataSource={fixedData}
      pagination={false}
      scroll={{ x: 200, y: 300 }}
      bordered
    />
  );
}
