pragma solidity ^0.4.25;




contract Poll {
    
    
    struct News{
        string headline;
        string body;
        address publisher_address;
        uint256 real_votes;
        uint256 fake_votes;
    }
    
    address news_station;
    string[] real_headlines;
    string current_headline;
    mapping(string=>News) metadata;
    mapping(address=>uint256) voter_balance;
    uint256 totalVotes;
    
    constructor() public{
        news_station = msg.sender;
    }
    
    modifier onlyOwner(){
        require(msg.sender == news_station);
        _;
    }
    
    // modifier hasNotVoted(){
    //     require(voted_list[msg.sender]==false);
    //     _;
    // }
    
    modifier voterHasBalance(){
        require(voter_balance[msg.sender]>0);
        _;
    }
    
    modifier PollIsEmpty{
        require(bytes(current_headline).length==0);
        _;
    }
    
    modifier NotPublisher(){
        require(msg.sender != metadata[current_headline].publisher_address);
        _;
    }
    
    function deposit() public payable onlyOwner{
        
    }
    
    function withdraw() public onlyOwner{
        news_station.transfer(address(this).balance);
    }
    
    function getBalance() public view onlyOwner returns(uint256){
        return(address(this).balance);
    }
    
    
    function getCurrent() public view returns(string){
        return(current_headline);
    }
    
    function getDetails() public voterHasBalance returns(string,uint256,uint256) {
        voter_balance[msg.sender] -= 1;
        return(metadata[current_headline].body,metadata[current_headline].real_votes,metadata[current_headline].fake_votes);
    }
    
    function submitHeadline(string _headline,string _body) public PollIsEmpty{
        require(bytes(_headline).length != 0 && bytes(_body).length!=0);
        
        current_headline = _headline;
        metadata[current_headline].body = _body;
        metadata[current_headline].publisher_address = msg.sender;
        // if(real_headlines.length)
        // real and fake votes already instantiated to 0
    }
    
    event Voted(address,bool);
    
    
    
    function Vote(bool _choice) public payable NotPublisher {
        require(msg.value >= 0.01 ether);
        if(_choice){
            metadata[current_headline].real_votes += 1;
        }
        else{
            metadata[current_headline].fake_votes += 1;
        }
        voter_balance[msg.sender] += 1;
        totalVotes = metadata[current_headline].real_votes + metadata[current_headline].fake_votes;
        
        // ensure that this guy has voted.
        emit Voted(msg.sender,true);
        
        if(totalVotes>=3){
            reset_poll();
        }
        
    }
    
    function reset_poll() internal {
        if((metadata[current_headline].real_votes/totalVotes) * 100 >= 60 ){
            real_headlines.push(current_headline);
            metadata[current_headline].publisher_address.transfer(5 ether);
        }
        
        delete current_headline;
        delete totalVotes;
        
    }
    
    
}
