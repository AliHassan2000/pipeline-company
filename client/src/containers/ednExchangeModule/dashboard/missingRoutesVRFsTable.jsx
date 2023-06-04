import React, { useState, useEffect, PureComponent } from "react";
import styled from "styled-components";
import { ResponsiveContainer, Tooltip, Legend } from "recharts";
import { LineChart, Line, XAxis, YAxis, CartesianGrid } from "recharts";
import axios, { baseUrl } from "../../../utils/axios";
import { Spin } from "antd";
import { CustomizedLabel } from "../../../utils/helpers";
import { StyledTable } from "../../../components/table/main.styles";
import useWindowDimensions from "../../../hooks/useWindowDimensions";
import { columnSearch } from "../../../utils";

let columnFilters = {};
let excelData = [];
const Index = ({}) => {
  const { height, width } = useWindowDimensions();
  const [rowCount, setRowCount] = useState(0);
  const [dataSource, setDataSource] = useState(null);
  const [searchText, setSearchText] = useState(null);
  const [searchedColumn, setSearchedColumn] = useState(null);
  const [loading, setLoading] = useState(false);

  let getColumnSearchProps = columnSearch(
    searchText,
    setSearchText,
    searchedColumn,
    setSearchedColumn
  );

  const handleChange = (pagination, filters, sorter, extra) => {
    console.log("Various parameters", pagination, filters, sorter, extra);
  };

  useEffect(() => {
    const serviceCalls = async () => {
      setLoading(true);
      try {
        axios.get(baseUrl + "/getVrfsWithMissingRoutesTable").then((res) => {
          excelData = res.data;
          setDataSource(res.data);
          setRowCount(res.length);
        });

        setLoading(false);
      } catch (err) {
        console.log(err.response);
        setLoading(false);
      }
    };
    serviceCalls();
  }, []);

  let columns = [
    {
      dataIndex: "vrf_name",
      key: "vrf_name",
      ...getColumnSearchProps(
        "vrf_name",
        "VRF Name",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      ellipsis: true,
    },
    {
      dataIndex: "primary_site",
      key: "primary_site",
      ...getColumnSearchProps(
        "primary_site",
        "Primary Site",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      ellipsis: true,
    },
    {
      dataIndex: "secondary_site",
      key: "secondary_site",
      ...getColumnSearchProps(
        "secondary_site",
        "Secondary Site",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      ellipsis: true,
    },
    {
      dataIndex: "no_of_received_routes",
      key: "no_of_received_routes",
      ...getColumnSearchProps(
        "no_of_received_routes",
        "No. of Received Routes",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      ellipsis: true,
    },
    {
      dataIndex: "missing_routes_in_secondary_site",
      key: "missing_routes_in_secondary_site",
      ...getColumnSearchProps(
        "missing_routes_in_secondary_site",
        "Missing Routes in Secondary Site",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      ellipsis: true,
    },
  ];

  return (
    <Spin spinning={loading}>
      <div>
        <StyledCard
          style={{
            color: "white",
            fontSize: "17px",
            backgroundColor: "#009bdb",
            borderBottomRightRadius: "0",
            borderBottomLeftRadius: "0",
            paddingTop: "6px",
            // opacity: "0.8",
            paddingBottom: "8px",
            fontWeight: "bold",
            // borderColor: "3px solid brown",
          }}
        >
          Extranet VRFs with Missing Routes
        </StyledCard>
        <StyledCard
          style={{
            // backgroundColor,
            height: "45vh",
            borderTopRightRadius: "0",
            borderTopLeftRadius: "0",
          }}
        >
          {dataSource ? (
            <StyledTable
              pagination={{
                defaultPageSize: 50,
                pageSizeOptions: [50, 100, 500, 1000],
              }}
              size="small"
              scroll={{ y: height - 550 }}
              onChange={handleChange}
              columns={columns}
              dataSource={dataSource}
              rowKey="user_id"
              style={{ whiteSpace: "pre", marginTop: 0, paddingTop: "10px" }}
            />
          ) : (
            <div
              style={{
                textAlign: "center",
                // border: "1px solid black",
                height: "100%",
                paddingTop: "15%",
              }}
            >
              <Spin tip="Loading Table..." spinning={true} />
            </div>
          )}
        </StyledCard>
      </div>
    </Spin>
  );
};

export default Index;

const StyledCard = styled.div`
  /* margin-top: -10px; */
  /* margin-bottom: 10px; */
  height: 100%;
  /* text-align: center; */
  background-color: white;
  border-radius: 10px;
  padding: 0px 20px 20px 20px;
  box-shadow: rgba(99, 99, 99, 0.2) 0px 2px 8px 0px;
`;
