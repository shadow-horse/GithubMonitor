import React from 'react';
import { PageHeaderWrapper } from '@ant-design/pro-layout';
import { FormattedMessage } from 'umi-plugin-react/locale';
import { Card, Typography, Alert, Input, Option, Select } from 'antd';
import styles from './index.less';
import FormCoordinated from './components/FormCoordinated';
import ScantaskList from './components/ScantaskList';


const { Search } = Input;

class ScanList extends React.Component {

    //组件定义
    scantaskList = [<ScantaskList/>];
    //设置this.state
    state = {
        acceptContent: '',
    };
    //接收子组件的信息
    receive(content) {

        this.setState(
            { acceptContent: content },
        );
        console.log(content);
        if (content['FormCoordinated'] !== undefined) {
            
            //当选择task后，重新刷新页面
            const id = content['FormCoordinated'];
            const status = content['status'];
            console.log('id', id);
            console.log('status', id);
            this.scantaskList = [];
            this.scantaskList.push(<ScantaskList id={id} status={status} />);
            this.setState();
        };
        
    }


    render() {
        return (
            <PageHeaderWrapper>
                <Card>
                    <FormCoordinated name="name" data="gettasklist" onSendmsg={this.receive.bind(this)} />
         
                   {this.scantaskList}
                </Card>
            </PageHeaderWrapper>

        );
    };
};

export default ScanList;