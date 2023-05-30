%ChronotateBatchAnalysis
clear
secondsToScore=Inf; %can set a cuttoff time for 'prefs' and 'expByCutoff' set it Inf to retun final values by the end of the last bout
excludes = {}; %unblinded file names of animals to be excluded

[FileName,PathName]=uigetfile('*.csv','Select Marker Files','Multiselect','on');
if ischar(FileName)
    FileName={FileName};
end

[KeyFile,KeyPath]=uigetfile('*.xlsx','Select File Name Key'); %key file contains original file names and aliases used for blinding along with group and which object was novel
fileKey  = readtable(fullfile(KeyPath,KeyFile));

for fileIdx = 1:length(FileName)
    markerFile=fullfile(PathName,FileName{fileIdx});
    
    alias = extractAfter(extractBefore(FileName{fileIdx},'Merged'),'_'); %FileName{fileIdx};%
    trueFile = fileKey.Original_File_Name{contains(fileKey.New_File_Name,alias)}; %alias;%
    group = fileKey.Group{contains(fileKey.New_File_Name,alias)};
    novelID = fileKey.novelID(contains(fileKey.New_File_Name,alias));
    
    groups{fileIdx} = group;
    novelIDs(fileIdx) = novelID;
    aliases{fileIdx} = alias;
    trueFiles{fileIdx} = trueFile;
    
    markerTab=readtable(markerFile);
    markerTab = sortrows(markerTab); %sorts markers by timestamp: important if bouts were marked after seeking backwards through the video
    
        numBouts = length(markerTab.marker_time)/2;
    objectID = markerTab.object_id(1:2:end);
    boutDur = markerTab.marker_time(2:2:end)-markerTab.marker_time(1:2:end);
    boutStart = markerTab.marker_time(1:2:end);
    boutEnd = markerTab.marker_time(2:2:end);
    cumulativeTotal=cumsum(boutDur);
    if novelID == 1
        familiarID = 2;
    else
        familiarID = 1;
    end
        
    cumulativeFamiliar=cumsum(boutDur(objectID==familiarID));
    cumulativeNovel=cumsum(boutDur(objectID==novelID));
    cumulativeFamiliarAll=zeros(size(objectID));
    cumulativeFamiliarAll(objectID==familiarID)=cumulativeFamiliar;
    cumulativeNovelAll=zeros(size(objectID));
    cumulativeNovelAll(objectID==novelID)=cumulativeNovel;

    for boutIdx = 2:numBouts
        if cumulativeFamiliarAll(boutIdx)==0
            cumulativeFamiliarAll(boutIdx)=cumulativeFamiliarAll(boutIdx-1);
        end

        if cumulativeNovelAll(boutIdx)==0
            cumulativeNovelAll(boutIdx)=cumulativeNovelAll(boutIdx-1);
        end
    end

    pref = cumulativeNovelAll./cumulativeTotal;

    boutTab=table(objectID, boutStart,boutEnd,boutDur,cumulativeTotal,cumulativeFamiliarAll,cumulativeNovelAll,pref, 'VariableNames',{'objectID' 'boutStart' 'boutEnd' 'boutDur' 'cumulativeTotal' 'cumulativeFamiliarAll' 'cumulativeNovelAll' 'pref'});
    activeSessionLen = floor(boutEnd(end));
    sessionTimes = 1:activeSessionLen;
    prefBySecond=[];
    expTot=[]; %total exploration by seconds in box
    novTot=[];
    famTot=[];
    for sessionSecond = sessionTimes
        if sessionSecond<boutStart(1)
        prefBySecond(sessionSecond) = 0;
        expTot(sessionSecond) = 0;
        novTot(sessionSecond) = 0;
        famTot(sessionSecond) = 0;
        else 
            afterBout = find(sessionSecond>=boutEnd(1:end-1)&sessionSecond<=boutStart(2:end),1); %current sescond is between two bouts, preference is whatever it was at the end of preceding bout
            if ~isempty(afterBout)
                prefBySecond(sessionSecond)=pref(afterBout);
                expTot(sessionSecond)=cumulativeTotal(afterBout);
                novTot(sessionSecond) = cumulativeNovelAll(afterBout);
                famTot(sessionSecond) = cumulativeFamiliarAll(afterBout);
            else
                withinBout = find(sessionSecond>=boutStart&sessionSecond<=boutEnd,1); %current sescond is within a bout, calculate pref
                boutProg = sessionSecond - boutStart(withinBout); %how many seconds into this bout are we
                if withinBout==1
                    prevExpTot=0;
                    prevNovTot=0;
                    prevFamTot=0;
                else
                    prevExpTot=cumulativeTotal(withinBout-1);
                    prevNovTot=cumulativeNovelAll(withinBout-1);
                    prevFamTot=cumulativeFamiliarAll(withinBout-1);
                end
                expTot(sessionSecond) = prevExpTot+boutProg; %add bout progress to total exploration 
                if objectID(withinBout) == novelID %if interacting with the novel this bout
                    novTot(sessionSecond) = prevNovTot + boutProg; %add to time spent with novel
                    famTot(sessionSecond) = prevFamTot; %time spent with familiar is same as end of last bout
                else
                    novTot(sessionSecond) = prevNovTot; %time spent with novel is same as end of last bout
                    famTot(sessionSecond) = prevFamTot + boutProg; %add to time spent with familiar
                end
                prefBySecond(sessionSecond)=novTot(sessionSecond)/expTot(sessionSecond);
            end    
        end
    end
    
     expTime = 1:floor(cumulativeTotal(end));
    prefExpPt=[];
    
    if ~isempty(expTime)
        for x = expTime
            boutInd = find(cumulativeTotal>=x,1);
            if objectID(boutInd) == familiarID
                prefExpPt(x) = cumulativeNovelAll(boutInd)/x;
            else
                prefExpPt(x) = (cumulativeNovelAll(boutInd)-(cumulativeTotal(boutInd)-x))/x;

            end
        end
        prefByExp{fileIdx} = prefExpPt;
    else
        prefByExp{fileIdx} = nan;
    end
    
    DIs{fileIdx}=((novTot-famTot)./expTot)*100;
    prefs(fileIdx)=prefBySecond(min(secondsToScore,activeSessionLen));
    expByCutoff(fileIdx)=expTot(min(secondsToScore,activeSessionLen));
    prefsBySeconds{fileIdx}=prefBySecond;
    expTots{fileIdx}=expTot;
    novTots{fileIdx}=novTot;
    famTots{fileIdx}=famTot;


   isExclude(fileIdx) = any(contains(excludes,trueFile));

    
    save(fullfile(PathName,[trueFile '_boutTab.mat']),'boutTab');
end

%generate average plot
prefTab=table(trueFiles', aliases', groups',novelIDs', prefByExp', prefsBySeconds', expTots', novTots', famTots', DIs', expByCutoff', prefs', isExclude', 'VariableNames',{'trueFiles', 'aliases', 'groups','novelIDs', 'prefByExp', 'prefsBySeconds', 'expTots', 'novTots', 'famTots', 'DIs', 'expByCutoff', 'prefs', 'isExclude'});
save(fullfile(KeyPath,[KeyFile '_prefTab.mat']),'prefTab');

prefColor=[0 0 197]/255;
expColor=[197 0 197]/255; 

WTtab=prefTab(contains(prefTab.groups,'Control')&~prefTab.isExclude,:);
wtTime=max(cellfun(@length, WTtab.DIs,'UniformOutput', true));
WTprefmat = cell2mat(cellfun(@(x) [x  x(end)*ones(1,wtTime-length(x))], WTtab.prefsBySeconds,'UniformOutput', false));

WTprefmean = nanmean(WTprefmat,1);
WTprefstd = std(WTprefmat,0,1,'omitnan');
WTprefsem = WTprefstd/sqrt(size(WTprefmat,1));

WTexpmat = cell2mat(cellfun(@(x) [x  x(end)*ones(1,wtTime-length(x))], WTtab.expTots,'UniformOutput', false));

WTexpmean = nanmean(WTexpmat,1);
WTexpstd = std(WTexpmat,0,1,'omitnan');
WTexpsem = WTexpstd/sqrt(size(WTexpstd,1));

figure;
yyaxis left
shadedErrorBar(1:wtTime,WTprefmean,WTprefsem,'lineprops',{'Color',prefColor,'LineWidth',3})
hold on;
plot(xlim,[.5,.5],'k--','LineWidth',3)

title('NOL Preference')

xlabel('Time in box(s)')
yyaxis left
ylabel('Cumulative Preference for Novel')
yyaxis right
ylabel('Cumulative Exploration(s)')

yyaxis right

shadedErrorBar(1:wtTime,WTexpmean,WTexpsem,'lineprops',{'Color',expColor,'LineWidth',3})

