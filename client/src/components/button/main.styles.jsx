import styled from "styled-components";
import { Button } from "antd";

export const StyledButton = styled(Button)`
  height: 25px;
  padding: 0px 12px 0 12px;
  font-size: 11px;
  font-family: Montserrat-Regular;
  font-weight: bolder;
  box-shadow: rgba(0, 0, 0, 0.24) 0px 3px 8px;
  background-color: ${(props) => props.color};
  border-color: ${(props) => props.color};
  color: white;
  border-radius: 3px;
  &:focus,
  &:hover {
    background-color: ${(props) => props.color};
    border-color: ${(props) => props.color};
    color: white;
    opacity: 0.8;
  }
`;
