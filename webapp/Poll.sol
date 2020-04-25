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
    uint256[] real_headlines;
    string current_headline;
    uint256 indexOfNews;
    mapping(uint256=>News) metadata;
    mapping(address=>uint256) voter_balance;
    uint256 totalVotes;
    mapping(address=>uint256) publisher_rewards;
    
    event Voted(address voter,bool voted);
    event Details(string body,uint256 real, uint256 fake, address pubisher);
    
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
        require(msg.sender != metadata[indexOfNews].publisher_address);
        _;
    }
    
    
    // Owner Function
    function deposit() public payable onlyOwner{
        
    }
    
    function withdraw() public onlyOwner{
        news_station.transfer(address(this).balance);
    }
    
    function getContractBalance() public view onlyOwner returns(uint256){
        return(address(this).balance);
    }
    
    function getVoterBalance() public view returns(uint256){
        return(voter_balance[msg.sender]);
    }
    
    
    function getCurrentHeadline() public view returns(string){
        return(current_headline);
    }
    
    
    function getHeadlineFromIndex(uint256 _index) public view returns(string){
        return(metadata[_index].headline);
    }
    
    function getTotalNumberOfNews() public view returns(uint256){
        return(indexOfNews);
    }
    
    function getOwner() public view returns(address){
        return(news_station);
    }
    
    function getPublisherBalance() public view returns(uint256){
        return(publisher_rewards[msg.sender]);
    }
    
    function getCurrentNewsDetails() public voterHasBalance returns(string,uint256,uint256) {
        voter_balance[msg.sender] -= 1;
        emit Details(metadata[indexOfNews].body,metadata[indexOfNews].real_votes,metadata[indexOfNews].fake_votes,metadata[indexOfNews].publisher_address);
        return(metadata[indexOfNews].body,metadata[indexOfNews].real_votes,metadata[indexOfNews].fake_votes);
    }
    
     function getSpecificNewsDetails(uint256 _index) public voterHasBalance returns(string,uint256,uint256) {
        voter_balance[msg.sender] -= 1;
        emit Details(metadata[_index].body,metadata[_index].real_votes,metadata[_index].fake_votes,metadata[_index].publisher_address);
        return(metadata[_index].body,metadata[_index].real_votes,metadata[_index].fake_votes);
    }
    
    function submitHeadline(string _headline,string _body) public PollIsEmpty{
        require(bytes(_headline).length != 0 && bytes(_body).length!=0);
        indexOfNews += 1;
        current_headline = _headline;
        metadata[indexOfNews].headline = current_headline;
        metadata[indexOfNews].body = _body;
        metadata[indexOfNews].publisher_address = msg.sender;
        // if(real_headlines.length)
        // real and fake votes already instantiated to 0
    }
    
    function claimReward(uint256 _value) public {
        require(_value<=publisher_rewards[msg.sender]);
        publisher_rewards[msg.sender] -= _value;
        msg.sender.transfer(_value*(1 ether));
        
        
    }
    
    
    function Vote(bool _choice) public payable NotPublisher {
        require(msg.value >= 0.01 ether);
        require(bytes(current_headline).length!=0);
        if(_choice){
            metadata[indexOfNews].real_votes += 1;
        }
        else{
            metadata[indexOfNews].fake_votes += 1;
        }
        voter_balance[msg.sender] += 1;
        totalVotes = metadata[indexOfNews].real_votes + metadata[indexOfNews].fake_votes;
        
        // ensure that this guy has voted.
        emit Voted(msg.sender,true);
        
        if(totalVotes>=2){
            reset_poll();
        }
        
    }
    
    function reset_poll() internal {
        if((metadata[indexOfNews].real_votes/totalVotes) * 100 >= 60 ){
            real_headlines.push(indexOfNews);
            // metadata[indexOfNews].publisher_address.transfer(2 ether);
            publisher_rewards[metadata[indexOfNews].publisher_address] += 2;
            
        }
        
        // kind of compensates the gas cause they pay for reset
        delete current_headline;
        delete totalVotes;
        
    }
    
}
