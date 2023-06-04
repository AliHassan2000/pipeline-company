import React, { useState, useEffect, useContext } from "react";
import { Table, Button, Checkbox, Spin, Menu, Dropdown } from "antd";
import Search from "../../../../components/search";
import { StyledTable } from "../../../../components/table/main.styles";
import { StyledHeading } from "../../../../components/paragraph/main.styles";
import axios, { baseUrl } from "../../../../utils/axios";
// import axios from "axios";
import { useLocation, useHistory } from "react-router-dom";
import { columnSearch } from "../../../../utils";
import useWindowDimensions from "../../../../hooks/useWindowDimensions";
import { Context } from "../../../../context";
import XLSX from "xlsx";
import { StyledButton } from "../../../../components/button/main.styles";
import {
  RightSquareOutlined,
  EditOutlined,
  DownOutlined,
} from "@ant-design/icons";
import Modal from "./modal";
import { roles } from "../../../../utils/constants";

let columnFilters = {};
let excelData = [];
const Index = (props) => {
  const { height, width } = useWindowDimensions();
  const history = useHistory();
  const { search } = useLocation();
  const searchParams = new URLSearchParams(search);
  // const { excelData, sfps, getSFPs, domain } = useContext(Context);
  const [user, setUser] = useState();
  let [sortedInfo, setSortedInfo] = useState(null);
  let [filteredInfo, setFilteredInfo] = useState(null);
  let [dataSource, setDataSource] = useState(null);
  let [searchValue, setSearchValue] = useState(null);
  let [exportLoading, setExportLoading] = useState(false);
  let [loading, setLoading] = useState(false);
  const [searchText, setSearchText] = useState(null);
  const [searchedColumn, setSearchedColumn] = useState(null);
  const [rowCount, setRowCount] = useState(0);
  let getColumnSearchProps = columnSearch(
    searchText,
    setSearchText,
    searchedColumn,
    setSearchedColumn
  );
  //---------------------------------------
  useEffect(() => {
    const serviceCalls = async () => {
      setLoading(true);
      setUser(JSON.parse(localStorage.getItem("user")));
      // try {
      //   if (
      //     sfps.length === 0 ||
      //     domain !==
      //       (searchParams.get("domain") === null
      //         ? "All"
      //         : searchParams.get("domain"))
      //   ) {
      //     let data = await getSFPs(searchParams.get("domain"));
      //     console.log(data);
      //     setRowCount(data.length);
      //     setDataSource(data);
      //   } else {
      //     setRowCount(sfps.length);
      //     setDataSource(sfps);
      //   }
      //   setLoading(false);
      // } catch (err) {
      //   console.log(err);
      //   setLoading(false);
      // }

      let domain = searchParams.get("domain");
      try {
        const res = await axios.get(
          `${baseUrl}/getAllSfps${
            domain === "All" || domain === null ? "" : domain
          }`
        );
        setDataSource(res.data);
        excelData = res.data;
        setRowCount(excelData.length);
        setLoading(false);
      } catch (err) {
        setLoading(false);
        console.log(err);
      }
    };
    serviceCalls();
  }, []);

  const handleChange = (pagination, filters, sorter, extra) => {
    console.log("Various parameters", pagination, filters, sorter);
    setRowCount(extra.currentDataSource.length);
    setFilteredInfo(filters);
    setSortedInfo(sorter);
  };

  const handleSeedInput = (e) => {
    let filteredSuggestions = excelData.filter(
      (d) =>
        JSON.stringify(d)
          .replace(" ", "")
          .toLowerCase()
          .indexOf(e.target.value.toLowerCase()) > -1
    );
    setRowCount(filteredSuggestions.length);
    setDataSource(filteredSuggestions);
  };

  sortedInfo = sortedInfo || {};
  filteredInfo = filteredInfo || {};

  const [editRecord, setEditRecord] = useState(null);
  const [isModalVisible, setIsModalVisible] = useState(false);

  const edit = (record) => {
    setEditRecord(record);
    showEditModal();
  };

  const showEditModal = () => {
    setIsModalVisible(true);
  };

  const columns = [
    {
      title: "",
      key: "edit",
      width: "35px",

      render: (text, record) => (
        <a>
          <EditOutlined
            onClick={() => {
              edit(record);
            }}
          />
        </a>
      ),
    },
    //-------------------------------------------
    {
      title: "SFP Id",
      dataIndex: "sfp_id",
      key: "sfp_id",
      // ...getColumnSearchProps("sfp_id"),
      ...getColumnSearchProps(
        "sfp_id",
        "SFP Id",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.sfp_id - b.sfp_id,
      // sortOrder: sortedInfo.columnKey === "sfp_id" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Serial Number",
      dataIndex: "serial_number",
      key: "serial_number",
      // ...getColumnSearchProps("sfp_id"),
      ...getColumnSearchProps(
        "serial_number",
        "Serial Number",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.sfp_id - b.sfp_id,
      // sortOrder: sortedInfo.columnKey === "sfp_id" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Device Id",
      dataIndex: "device_id",
      key: "device_id",
      // ...getColumnSearchProps("device_id"),
      ...getColumnSearchProps(
        "device_id",
        "Device Id",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.device_id.length - b.device_id.length,
      // sortOrder: sortedInfo.columnKey === "device_id" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Port Name",
      dataIndex: "port_name",
      key: "port_name",
      // ...getColumnSearchProps("port_name"),
      ...getColumnSearchProps(
        "port_name",
        "Port Name",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.port_name - b.port_name,
      // sortOrder: sortedInfo.columnKey === "port_name" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Pn Code",
      dataIndex: "pn_code",
      key: "pn_code",
      // ...getColumnSearchProps("pn_code"),
      ...getColumnSearchProps(
        "pn_code",
        "Pn Code",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.pn_code.length - b.pn_code.length,
      // sortOrder: sortedInfo.columnKey === "pn_code" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "EOS Date",
      dataIndex: "eos_date",
      key: "eos_date",
      // ...getColumnSearchProps("eos_date"),
      ...getColumnSearchProps(
        "eos_date",
        "EOS Date",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.eos_date.length - b.eos_date.length,
      // sortOrder: sortedInfo.columnKey === "eos_date" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "EOL Date",
      dataIndex: "eol_date",
      key: "eol_date",
      // ...getColumnSearchProps("eol_date"),
      ...getColumnSearchProps(
        "eol_date",
        "EOL Date",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.eol_date.length - b.eol_date.length,
      // sortOrder: sortedInfo.columnKey === "eol_date" && sortedInfo.order,
      ellipsis: true,
    },
    {
      dataIndex: "item_code",
      key: "item_code",
      // ...getColumnSearchProps("authentication"),
      ...getColumnSearchProps(
        "item_code",
        "Item Code",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.authentication.length - b.authentication.length,
      // sortOrder: sortedInfo.columnKey === "authentication" && sortedInfo.order,
      ellipsis: true,
    },
    {
      dataIndex: "item_desc",
      key: "item_desc",
      // ...getColumnSearchProps("authentication"),
      ...getColumnSearchProps(
        "item_desc",
        "Item Desc",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.authentication.length - b.authentication.length,
      // sortOrder: sortedInfo.columnKey === "authentication" && sortedInfo.order,
      ellipsis: true,
    },
    {
      dataIndex: "clei",
      key: "clei",
      // ...getColumnSearchProps("authentication"),
      ...getColumnSearchProps(
        "clei",
        "Clei",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.authentication.length - b.authentication.length,
      // sortOrder: sortedInfo.columnKey === "authentication" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Tag Id",
      dataIndex: "tag_id",
      key: "tag_id",
      // ...getColumnSearchProps("tag_id"),
      ...getColumnSearchProps(
        "tag_id",
        "Tag Id",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.tag_id.length - b.tag_id.length,
      // sortOrder: sortedInfo.columnKey === "tag_id" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "RFS Date",
      dataIndex: "rfs_date",
      key: "rfs_date",
      // ...getColumnSearchProps("rfs_date"),
      ...getColumnSearchProps(
        "rfs_date",
        "RFS Date",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.rfs_date.length - b.rfs_date.length,
      // sortOrder: sortedInfo.columnKey === "rfs_date" && sortedInfo.order,
      ellipsis: true,
    },
    {
      dataIndex: "dismantle_date",
      key: "dismantle_date",
      // ...getColumnSearchProps("rfs_date"),
      ...getColumnSearchProps(
        "dismantle_date",
        "Dismantle Date",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.rfs_date.length - b.rfs_date.length,
      // sortOrder: sortedInfo.columnKey === "rfs_date" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Speed",
      dataIndex: "speed",
      key: "speed",
      // ...getColumnSearchProps("speed"),
      ...getColumnSearchProps(
        "speed",
        "Speed",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.speed.length - b.speed.length,
      // sortOrder: sortedInfo.columnKey === "speed" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Manufacturer",
      dataIndex: "manufacturer",
      key: "manufacturer",
      // ...getColumnSearchProps("manufacturer"),
      ...getColumnSearchProps(
        "manufacturer",
        "Manufacturer",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.manufacturer.length - b.manufacturer.length,
      // sortOrder: sortedInfo.columnKey === "manufacturer" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Wave Length",
      dataIndex: "wavelength",
      key: "wavelength",
      // it may have no in  wavelength
      // ...getColumnSearchProps("wavelength"),
      ...getColumnSearchProps(
        "wavelength",
        "Wave Length",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.manufacturer.length - b.manufacturer.length,
      // sortOrder: sortedInfo.columnKey === "wavelength" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Status",
      dataIndex: "status",
      key: "status",
      // ...getColumnSearchProps("status"),
      ...getColumnSearchProps(
        "status",
        "Status",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.region.length - b.region.length,
      // sortOrder: sortedInfo.columnKey === "region" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Optical Direction Type",
      dataIndex: "optical_direction_type",
      key: "optical_direction_type",
      // ...getColumnSearchProps("optical_direction_type"),
      ...getColumnSearchProps(
        "optical_direction_type",
        "Optical Direction Type",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.optical_direction_type - b.optical_direction_type,
      // sortOrder:
      //   sortedInfo.columnKey === "optical_direction_type" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Media Type",
      dataIndex: "media_type",
      key: "media_type",
      // ...getColumnSearchProps("media_type"),
      ...getColumnSearchProps(
        "media_type",
        "Media Type",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.media_type - b.media_type,
      // sortOrder: sortedInfo.columnKey === "media_type" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Port Type",
      dataIndex: "port_type",
      key: "port_type",
      // ...getColumnSearchProps("port_type"),
      ...getColumnSearchProps(
        "port_type",
        "Port Type",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.port_type.length - b.port_type.length,
      // sortOrder: sortedInfo.columnKey === "port_type" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Connector",
      dataIndex: "connector",
      key: "connector",
      // ...getColumnSearchProps("connector"),
      ...getColumnSearchProps(
        "connector",
        "Connector",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.connector.length - b.connector.length,
      // sortOrder: sortedInfo.columnKey === "connector" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Mode",
      dataIndex: "mode",
      key: "mode",
      // ...getColumnSearchProps("mode"),
      ...getColumnSearchProps(
        "mode",
        "Mode",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.mode.length - b.mode.length,
      // sortOrder: sortedInfo.columnKey === "mode" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Creation Date",
      dataIndex: "creation_date",
      key: "creation_date",
      // ...getColumnSearchProps("creation_date"),
      ...getColumnSearchProps(
        "creation_date",
        "Creation Date",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.creation_date.length - b.creation_date.length,
      // sortOrder: sortedInfo.columnKey === "creation_date" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Modification Date",
      dataIndex: "modification_date",
      key: "modification_date",
      // ...getColumnSearchProps("modification_date"),
      ...getColumnSearchProps(
        "modification_date",
        "Modification Date",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.modification_date.length - b.modification_date.length,
      // sortOrder:
      //   sortedInfo.columnKey === "modification_date" && sortedInfo.order,
      ellipsis: true,
    },
    {
      dataIndex: "created_by",
      key: "created_by",
      // ...getColumnSearchProps("modification_date"),
      ...getColumnSearchProps(
        "created_by",
        "Created By",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.modification_date.length - b.modification_date.length,
      // sortOrder:
      //   sortedInfo.columnKey === "modification_date" && sortedInfo.order,
      ellipsis: true,
      hidden: user?.user_role !== roles.admin,
    },
    {
      dataIndex: "modified_by",
      key: "modified_by",
      // ...getColumnSearchProps("modification_date"),
      ...getColumnSearchProps(
        "modified_by",
        "Modified By",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.modification_date.length - b.modification_date.length,
      // sortOrder:
      //   sortedInfo.columnKey === "modification_date" && sortedInfo.order,
      ellipsis: true,
      hidden: user?.user_role !== roles.admin,
    },
  ].filter((item) => !item.hidden);

  const jsonToExcel = (seedData) => {
    let wb = XLSX.utils.book_new();
    let binarySeedData = XLSX.utils.json_to_sheet(seedData);
    XLSX.utils.book_append_sheet(wb, binarySeedData, "sfps");
    XLSX.writeFile(wb, "sfps.xlsx");
    setExportLoading(false);
  };

  const exportSeed = async () => {
    setExportLoading(true);
    jsonToExcel(excelData);
    setExportLoading(false);
  };

  const exportFiltered = async () => {
    setExportLoading(true);
    jsonToExcel(dataSource, "filteredednmaclegacy.xlsx");
    setExportLoading(false);
  };

  const menu = (
    <Menu style={{ marginTop: "-220px", height: "90px" }}>
      <Menu.Item
        key="0"
        style={{ backgroundColor: "transparent", padding: "0px 10px" }}
      >
        <StyledButton
          color={"#3bbdc2"}
          onClick={exportSeed}
          style={{ width: "100%" }}
        >
          <RightSquareOutlined /> Export All
        </StyledButton>
      </Menu.Item>
      <Menu.Item
        key="1"
        style={{ backgroundColor: "transparent", padding: "5px 10px" }}
      >
        <StyledButton
          color={"#3bbdc2"}
          onClick={exportFiltered}
          style={{ width: "100%" }}
        >
          <RightSquareOutlined /> Export Filtered
        </StyledButton>
      </Menu.Item>
    </Menu>
  );

  return (
    <>
      <Spin tip="Loading..." spinning={loading}>
        {isModalVisible && (
          <Modal
            isModalVisible={isModalVisible}
            setIsModalVisible={setIsModalVisible}
            dataSource={dataSource}
            setDataSource={setDataSource}
            excelData={excelData}
            setRowCount={setRowCount}
            editRecord={editRecord}
          />
        )}

        <StyledHeading>
          SFPs
          <span
            style={{
              float: "right",
              fontSize: "14px",
              fontWeight: "bold",
              color: "grey",
              paddingTop: "10px",
            }}
          >
            Rows: {rowCount} &nbsp;&nbsp;&nbsp; Columns: {columns.length - 1}
          </span>
        </StyledHeading>

        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            padding: "0 0 10px 0",
          }}
        >
          <Search searchValue={searchValue} handleSeedInput={handleSeedInput} />
        </div>

        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            padding: "0 0 10px 0",
          }}
        >
          <div></div>
          <div>
            <Spin spinning={exportLoading}>
              <Dropdown overlay={menu} trigger={["click"]}>
                <StyledButton color={"#3bbdc2"}>
                  Export
                  <DownOutlined />
                </StyledButton>
              </Dropdown>
            </Spin>
          </div>
        </div>

        <StyledTable
          pagination={{
            defaultPageSize: 50,
            pageSizeOptions: [50, 100, 500, 1000],
          }}
          scroll={{ x: 5000, y: height - 350 }}
          columns={columns}
          dataSource={dataSource}
          onChange={handleChange}
        />
      </Spin>
    </>
  );
};

export default Index;
