
function [imgRecovered, watermark] = cnn_expansion_extract(imgW, predictedImage, oddOrEvenNum)

%----------扩展嵌入反向提取与恢复方法-----------

imgW = double(imgW);
[M,N]=size(imgW);
mn=nextpow2(M*N);
imgRecovered = imgW;

oddOrEvenPlace = zeros(M,N);
for i=2:M-1
    for j=2:N-1
        if mod((i+j),2)==oddOrEvenNum
            oddOrEvenPlace(i,j)=1;
        end
    end
end
inserablePlace = find((oddOrEvenPlace==1));

metadataPrefix = [];
for k=length(inserablePlace):-1:length(inserablePlace)-mn+1
    metadataPrefix(length(inserablePlace)-k+1) = bitget(imgW(inserablePlace(k)),1);
end
compressedLocationMapLength = bitlist2num_local(metadataPrefix);
lsbToReplaceLength = compressedLocationMapLength + 4*mn;

lsbToReplaceBitlist = [];
for k=length(inserablePlace):-1:length(inserablePlace)-lsbToReplaceLength+1
    lsbToReplaceBitlist(length(inserablePlace)-k+1) = bitget(imgW(inserablePlace(k)),1);
end

startIndex = 1;
lengthCompressedLocationMapBitlist = lsbToReplaceBitlist(startIndex:startIndex+mn-1);
startIndex = startIndex + mn;
compressedLocationMapLength = bitlist2num_local(lengthCompressedLocationMapBitlist);

compressedLocationMapBitlist = lsbToReplaceBitlist(startIndex:startIndex+compressedLocationMapLength-1);
startIndex = startIndex + compressedLocationMapLength;
messageToEmbedLength = bitlist2num_local(lsbToReplaceBitlist(startIndex:startIndex+mn-1));
startIndex = startIndex + mn;
number1 = bitlist2num_local(lsbToReplaceBitlist(startIndex:startIndex+mn-1));
startIndex = startIndex + mn;
number0 = bitlist2num_local(lsbToReplaceBitlist(startIndex:startIndex+mn-1));

if number1==0
    locationMap = zeros(M,N);
else
    decodedLocationMap = arithdeco(compressedLocationMapBitlist, [number0, number1], M*N);
    locationMap = reshape(decodedLocationMap - 1, M, N);
end

messageToEmbed = [];
indexMessage = 1;
for k=1:length(inserablePlace)
    i = mod(inserablePlace(k),M);
    j = ceil(inserablePlace(k)/M);
    if locationMap(i,j)==0
        xWatermarked = imgRecovered(i,j);
        xPredict = predictedImage(i,j);
        Dij = xWatermarked - xPredict;
        messageToEmbed(indexMessage) = mod(Dij, 2);
        dij = floor(Dij / 2);
        imgRecovered(inserablePlace(k)) = dij + xPredict;
        indexMessage = indexMessage + 1;
        if indexMessage > messageToEmbedLength
            break;
        end
    end
end

extractedLsbBitlist = messageToEmbed(1:lsbToReplaceLength);
watermark = messageToEmbed(lsbToReplaceLength+1:messageToEmbedLength);

for k=length(inserablePlace):-1:length(inserablePlace)-lsbToReplaceLength+1
    bitIndex = length(inserablePlace)-k+1;
    imgRecovered(inserablePlace(k)) = imgRecovered(inserablePlace(k)) ...
        - bitget(imgRecovered(inserablePlace(k)),1) ...
        + extractedLsbBitlist(bitIndex);
end

end

function value = bitlist2num_local(bitlist)
value = 0;
for idx=1:length(bitlist)
    value = value * 2 + bitlist(idx);
end
end
