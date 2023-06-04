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
import { StyledButton } from "../../../../components/button/main.styles";
import { Context } from "../../../../context";
import Modal from "./editRack";
import AddModal from "./addRack";
import XLSX from "xlsx";
import {
  RightSquareOutlined,
  PlusOutlined,
  EditOutlined,
  DownOutlined,
} from "@ant-design/icons";
import RackDevicesModal from "./rackDevices";
import { roles } from "../../../../utils/constants";

let columnFilters = {};
let excelData = [];
const Index = (props) => {
  const { height, width } = useWindowDimensions();
  const history = useHistory();
  const { search } = useLocation();
  const searchParams = new URLSearchParams(search);
  // const { excelData, racks, getRacks, domain } = useContext(Context);
  const [user, setUser] = useState();
  let [sortedInfo, setSortedInfo] = useState(null);
  let [filteredInfo, setFilteredInfo] = useState(null);
  let [syncLoading, setSyncLoading] = useState(false);
  let [dataSource, setDataSource] = useState(null);
  let [searchValue, setSearchValue] = useState(null);
  let [exportLoading, setExportLoading] = useState(false);
  let [loading, setLoading] = useState(false);
  const [searchText, setSearchText] = useState(null);
  const [searchedColumn, setSearchedColumn] = useState(null);
  const [rowCount, setRowCount] = useState(0);
  const [editRecord, setEditRecord] = useState(null);
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [isRDModalVisible, setIsRDModalVisible] = useState(false);
  const [rDData, setRDData] = useState(null);

  // const [isAddModalVisible, setIsAddModalVisible] = useState(false);
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
      //     racks.length === 0 ||
      //     domain !==
      //       (searchParams.get("domain") === null
      //         ? "All"
      //         : searchParams.get("domain"))
      //   ) {
      //     let data = await getRacks(searchParams.get("domain"));
      //     console.log(data);
      //     setRowCount(data.length);
      //     setDataSource(data);
      //   } else {
      //     setRowCount(racks.length);
      //     setDataSource(racks);
      //   }
      //   setLoading(false);
      // } catch (err) {
      //   console.log(err);
      //   setLoading(false);
      // }

      let domain = searchParams.get("domain");
      try {
        const res = await axios.get(
          `${baseUrl}/getAllRacks${
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

  const edit = (record) => {
    setEditRecord(record);
    setIsModalVisible(true);
  };

  const showRackDevices = async (record) => {
    console.log(record);
    try {
      setLoading(true);
      const res = await axios.get(
        `${baseUrl}/getDevicesByRackId?rackid=${record.rack_id}`
      );
      console.log(res.data);
      setRDData(res.data);
      setIsRDModalVisible(true);
      setLoading(false);
    } catch (err) {
      setLoading(false);
      console.log(err);
    }
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
    {
      title: "Rack Id",
      dataIndex: "rack_id",
      key: "rack_id",
      // ...getColumnSearchProps("rack_id"),
      ...getColumnSearchProps(
        "rack_id",
        "Rack Id",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),

      render: (text, record) => (
        <a
          onClick={() => {
            showRackDevices(record);
          }}
        >
          {text}
        </a>
      ),
      // sorter: (a, b) => a.rack_id - b.rack_id,
      // sortOrder: sortedInfo.columnKey === "rack_id" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Rack Name",
      dataIndex: "rack_name",
      key: "rack_name",
      // ...getColumnSearchProps("rack_name"),
      ...getColumnSearchProps(
        "rack_name",
        "Rack Name",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),

      // sorter: (a, b) => a.rack_name.length - b.rack_name.length,
      // sortOrder: sortedInfo.columnKey === "rack_name" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Site Id",
      dataIndex: "site_id",
      key: "site_id",
      // ...getColumnSearchProps("site_id"),
      ...getColumnSearchProps(
        "site_id",
        "Site Id",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.site_id - b.site_id,
      // sortOrder: sortedInfo.columnKey === "site_id" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Manufacture Date",
      dataIndex: "manufactuer_date",
      key: "manufactuer_date",
      // ...getColumnSearchProps("manufactuer_date"),
      ...getColumnSearchProps(
        "manufactuer_date",
        "Manufacture Date",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.manufactuer_date.length - b.manufactuer_date.length,
      // sortOrder:
      //   sortedInfo.columnKey === "manufactuer_date" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Unit Position",
      dataIndex: "unit_position",
      key: "unit_position",
      // ...getColumnSearchProps("unit_position"),
      ...getColumnSearchProps(
        "unit_position",
        "Unit Position",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.unit_position.length - b.unit_position.length,
      // sortOrder: sortedInfo.columnKey === "unit_position" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Rack Model",
      dataIndex: "rack_model",
      key: "rack_model",
      // ...getColumnSearchProps("rack_model"),
      ...getColumnSearchProps(
        "rack_model",
        "Rack Model",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.rack_model.length - b.rack_model.length,
      // sortOrder: sortedInfo.columnKey === "rack_model" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "PN Code",
      dataIndex: "pn_code",
      key: "pn_code",
      // ...getColumnSearchProps("pn_code"),
      ...getColumnSearchProps(
        "pn_code",
        "PN Code",
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
      title: "Serial Number",
      dataIndex: "serial_number",
      key: "serial_number",
      // ...getColumnSearchProps("serial_number"),
      ...getColumnSearchProps(
        "serial_number",
        "Serial Number",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.serial_number.length - b.serial_number.length,
      // sortOrder: sortedInfo.columnKey === "serial_number" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Ru",
      dataIndex: "ru",
      key: "ru",
      // ...getColumnSearchProps("ru"),
      ...getColumnSearchProps(
        "ru",
        "Ru",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.ru.length - b.ru.length,
      // sortOrder: sortedInfo.columnKey === "ru" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "RFS",
      dataIndex: "rfs_date",
      key: "rfs_date",
      // ...getColumnSearchProps("rfs_date"),
      ...getColumnSearchProps(
        "rfs_date",
        "RFS",
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
      title: "Height",
      dataIndex: "height",
      key: "height",
      // ...getColumnSearchProps("height"),
      ...getColumnSearchProps(
        "height",
        "Height",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.height.length - b.height.length,
      // sortOrder: sortedInfo.columnKey === "height" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Width",
      dataIndex: "width",
      key: "width",
      // ...getColumnSearchProps("width"),
      ...getColumnSearchProps(
        "width",
        "Width",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.width.length - b.width.length,
      // sortOrder: sortedInfo.columnKey === "width" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Depth",
      dataIndex: "depth",
      key: "depth",
      // ...getColumnSearchProps("depth"),
      ...getColumnSearchProps(
        "depth",
        "Depth",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.depth.length - b.depth.length,
      // sortOrder: sortedInfo.columnKey === "depth" && sortedInfo.order,
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
      title: "Floor",
      dataIndex: "floor",
      key: "floor",
      // ...getColumnSearchProps("floor"),
      ...getColumnSearchProps(
        "floor",
        "Floor",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.floor.length - b.floor.length,
      // sortOrder: sortedInfo.columnKey === "floor" && sortedInfo.order,
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
      title: "Total Devices",
      dataIndex: "total_devices",
      key: "total_devices",
      // ...getColumnSearchProps("status"),
      ...getColumnSearchProps(
        "total_devices",
        "Total Devices",
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

  const showModal = () => {
    setEditRecord(null);
    setIsModalVisible(true);
  };

  const jsonToExcel = (seedData) => {
    let wb = XLSX.utils.book_new();
    let binarySeedData = XLSX.utils.json_to_sheet(seedData);
    XLSX.utils.book_append_sheet(wb, binarySeedData, "racks");
    XLSX.writeFile(wb, "racks.xlsx");
    setExportLoading(false);
  };

  const exportSeed = async () => {
    setExportLoading(true);
    jsonToExcel(excelData);
    setExportLoading(false);
  };

  const sync = async () => {
    setSyncLoading(true);
    await axios
      .get(baseUrl + "/addCountRackIdDevices")
      .then((response) => {
        setSyncLoading(false);
      })
      .catch((err) => {
        console.log(err);
        setSyncLoading(false);
      });
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
        {/* {isModalVisible && (
          <Modal
            isModalVisible={isModalVisible}
            setIsModalVisible={setIsModalVisible}
            dataSource={dataSource}
            setDataSource={setDataSource}
            editRecord={editRecord}
          />
        )} */}

        {isModalVisible && (
          <AddModal
            isModalVisible={isModalVisible}
            setIsModalVisible={setIsModalVisible}
            dataSource={dataSource}
            setDataSource={setDataSource}
            excelData={excelData}
            setRowCount={setRowCount}
            editRecord={editRecord}
          />
        )}

        {isRDModalVisible && (
          <RackDevicesModal
            isRDModalVisible={isRDModalVisible}
            setIsRDModalVisible={setIsRDModalVisible}
            data={rDData}
          />
        )}

        <StyledHeading>
          Racks
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
          <StyledButton onClick={showModal} color={"#009BDB"}>
            <PlusOutlined /> &nbsp; Add Rack
          </StyledButton>
        </div>

        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            padding: "0 0 10px 0",
          }}
        >
          <div>
            {/* <Spin spinning={syncLoading}>
              <StyledButton color={"#3bbdc2"} onClick={sync}>
                <RightSquareOutlined /> &nbsp; Sync Device Count
              </StyledButton>
            </Spin> */}
          </div>
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
          scroll={{ x: 4000, y: height - 350 }}
          columns={columns}
          dataSource={dataSource}
          onChange={handleChange}
        />
      </Spin>
    </>
  );
};

export default Index;
