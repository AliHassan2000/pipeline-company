import styled from "styled-components";
import { Table } from "antd";

export const StyledTable = styled(Table)`
  margin-top: 10px;
  .ant-table-container {
    .ant-table-content {
      table {
        thead.ant-table-thead {
          tr {
            th.ant-table-cell {
              font-size: 12px;
              margin: 0 !important;
              padding: 0 !important;
              padding: 5px 10px 5px 10px !important;
              font-family: "Montserrat-Regular";
              font-weight: 600;
            }
          }
        }
        tbody.ant-table-tbody {
          tr.ant-table-row {
            td.ant-table-cell {
              font-size: 11px !important;
              margin: 0 !important;
              padding: 0 !important;
              padding-left: 10px !important;
              height: ${(p) => p.cellHeight || "33px"} !important;
            }
          }
          tr.dark {
          }
          tr.light {
          }
        }
      }
    }
  }
`;
